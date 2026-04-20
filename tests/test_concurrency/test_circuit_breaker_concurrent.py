import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from hermes_core.utils.circuit_breaker import CircuitBreaker, CircuitState


class TestCircuitBreakerConcurrent:
    def test_concurrent_failures(self):
        breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

        def record_fail():
            breaker.record_failure()

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(record_fail) for _ in range(20)]
            for f in as_completed(futures):
                f.result()

        assert breaker.state == CircuitState.OPEN

    def test_concurrent_call_mixed(self):
        breaker = CircuitBreaker(failure_threshold=10, recovery_timeout=60)
        success_count = 0
        fail_count = 0
        lock = threading.Lock()

        def call_success():
            nonlocal success_count
            try:
                breaker.call(lambda: "ok")
                with lock:
                    success_count += 1
            except RuntimeError:
                with lock:
                    fail_count += 1

        def call_failure():
            nonlocal fail_count
            try:
                breaker.call(lambda: (_ for _ in ()).throw(Exception("fail")))
            except Exception:
                with lock:
                    fail_count += 1

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            for i in range(20):
                if i % 3 == 0:
                    futures.append(executor.submit(call_failure))
                else:
                    futures.append(executor.submit(call_success))
            for f in as_completed(futures):
                f.result()

        assert breaker.state in (CircuitState.OPEN, CircuitState.CLOSED)

    def test_concurrent_state_consistency(self):
        breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

        def mixed_operations():
            for _ in range(10):
                breaker.record_failure()
                state = breaker.state
                assert state in (CircuitState.CLOSED, CircuitState.OPEN, CircuitState.HALF_OPEN)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(mixed_operations) for _ in range(5)]
            for f in as_completed(futures):
                f.result()

        assert breaker.state == CircuitState.OPEN
