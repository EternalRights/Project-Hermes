import enum
import threading
import time


class CircuitState(enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0, half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._half_open_calls = 0
        self._lock = threading.Lock()

    def get_state(self) -> CircuitState:
        with self._lock:
            self._check_state_transition()
            return self._state

    def is_available(self) -> bool:
        with self._lock:
            self._check_state_transition()
            return self._state != CircuitState.OPEN

    def _check_state_transition(self):
        if self._state == CircuitState.OPEN:
            if time.monotonic() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
                self._success_count = 0

    def record_success(self):
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.half_open_max_calls:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    self._half_open_calls = 0
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0

    def record_failure(self):
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                self._half_open_calls = 0
                self._success_count = 0
            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self.failure_threshold:
                    self._state = CircuitState.OPEN

    def call(self, func, *args, **kwargs):
        with self._lock:
            self._check_state_transition()
            if self._state == CircuitState.OPEN:
                raise RuntimeError("Circuit breaker is OPEN")
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.half_open_max_calls:
                    raise RuntimeError("Circuit breaker HALF_OPEN max calls reached")
                self._half_open_calls += 1
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception:
            self.record_failure()
            raise

    @property
    def state(self) -> CircuitState:
        return self.get_state()

    @property
    def failure_count(self) -> int:
        with self._lock:
            return self._failure_count

    @property
    def success_count(self) -> int:
        with self._lock:
            return self._success_count

    @property
    def last_failure_time(self) -> float:
        with self._lock:
            return self._last_failure_time
