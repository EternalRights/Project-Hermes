import threading
import time


class TokenBucketRateLimiter:

    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self._tokens = float(capacity)
        self._last_time = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self._last_time
        new_tokens = elapsed * self.rate
        self._tokens = min(self.capacity, self._tokens + new_tokens)
        self._last_time = now

    def acquire(self, tokens: int = 1) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False

    def wait(self, tokens: int = 1) -> float:
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return 0.0
            needed = tokens - self._tokens
            wait_time = needed / self.rate
            self._tokens = 0.0
            self._last_time = time.monotonic() + wait_time
        time.sleep(wait_time)
        with self._lock:
            self._tokens = 0.0
            self._last_time = time.monotonic()
        return wait_time
