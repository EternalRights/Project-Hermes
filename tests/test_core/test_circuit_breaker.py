import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

from hermes_core.utils.circuit_breaker import CircuitBreaker, CircuitState

import pytest


@pytest.fixture
def breaker():
    return CircuitBreaker(failure_threshold=3, recovery_timeout=0.1, half_open_max_calls=2)


def test_circuit_breaker_closed_state(breaker):
    assert breaker.state == CircuitState.CLOSED
    assert breaker.is_available() is True
    func = MagicMock(return_value="ok")
    result = breaker.call(func)
    assert result == "ok"
    assert breaker.state == CircuitState.CLOSED


def test_circuit_breaker_open_state(breaker):
    for _ in range(3):
        breaker.record_failure()
    assert breaker.state == CircuitState.OPEN
    assert breaker.is_available() is False
    with pytest.raises(RuntimeError, match="OPEN"):
        breaker.call(MagicMock())


def test_circuit_breaker_half_open_recovery(breaker):
    for _ in range(3):
        breaker.record_failure()
    assert breaker.state == CircuitState.OPEN
    time.sleep(0.2)
    assert breaker.state == CircuitState.HALF_OPEN
    func = MagicMock(return_value="ok")
    result = breaker.call(func)
    assert result == "ok"
    result = breaker.call(func)
    assert result == "ok"
    assert breaker.state == CircuitState.CLOSED


def test_circuit_breaker_state_transition(breaker):
    assert breaker.state == CircuitState.CLOSED
    breaker.record_failure()
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 1
    breaker.record_failure()
    assert breaker.failure_count == 2
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN
    assert breaker.failure_count == 3
    time.sleep(0.2)
    assert breaker.state == CircuitState.HALF_OPEN
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN


def test_circuit_breaker_half_open_max_calls():
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1, half_open_max_calls=2)
    for _ in range(3):
        breaker.record_failure()
    assert breaker.state == CircuitState.OPEN
    time.sleep(0.2)
    assert breaker.state == CircuitState.HALF_OPEN

    def slow_func():
        time.sleep(0.5)
        return "ok"

    errors = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(breaker.call, slow_func) for _ in range(3)]
        for f in futures:
            try:
                f.result()
            except RuntimeError as e:
                errors.append(str(e))
    assert any("HALF_OPEN max calls" in e for e in errors)


def test_circuit_breaker_concurrent_failures():
    breaker = CircuitBreaker(failure_threshold=10, recovery_timeout=30.0, half_open_max_calls=2)
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(breaker.record_failure) for _ in range(20)]
        for f in futures:
            f.result()
    assert breaker.state == CircuitState.OPEN


def test_circuit_breaker_record_success_in_closed():
    breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30.0, half_open_max_calls=2)
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.failure_count == 2
    breaker.record_success()
    assert breaker.failure_count == 0


def test_circuit_breaker_properties():
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1, half_open_max_calls=2)
    assert breaker.failure_count == 0
    assert breaker.success_count == 0
    assert breaker.last_failure_time == 0.0
    breaker.record_failure()
    assert breaker.failure_count == 1
    assert breaker.last_failure_time > 0.0
    for _ in range(2):
        breaker.record_failure()
    assert breaker.state == CircuitState.OPEN
    time.sleep(0.2)
    assert breaker.state == CircuitState.HALF_OPEN
    breaker.record_success()
    assert breaker.success_count == 1
