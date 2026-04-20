import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from hermes_core.utils.rate_limiter import TokenBucketRateLimiter


class TestRateLimiterConcurrent:
    def test_concurrent_acquire(self):
        limiter = TokenBucketRateLimiter(rate=100, capacity=50)
        acquired_count = 0
        lock = threading.Lock()

        def try_acquire():
            nonlocal acquired_count
            if limiter.acquire():
                with lock:
                    acquired_count += 1

        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(try_acquire) for _ in range(100)]
            for f in as_completed(futures):
                f.result()

        assert acquired_count <= 55
        assert acquired_count >= 1

    def test_concurrent_wait(self):
        limiter = TokenBucketRateLimiter(rate=1000, capacity=5)
        for _ in range(5):
            limiter.acquire()

        results = []

        def try_wait():
            wait_time = limiter.wait(1)
            results.append(wait_time)

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(try_wait) for _ in range(3)]
            for f in as_completed(futures):
                f.result()

        assert len(results) == 3
        assert all(w >= 0 for w in results)

    def test_acquire_tokens_concurrent(self):
        limiter = TokenBucketRateLimiter(rate=10, capacity=20)
        acquired = 0
        lock = threading.Lock()

        def try_acquire_tokens():
            nonlocal acquired
            if limiter.acquire(tokens=5):
                with lock:
                    acquired += 5

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(try_acquire_tokens) for _ in range(10)]
            for f in as_completed(futures):
                f.result()

        assert acquired <= 25
