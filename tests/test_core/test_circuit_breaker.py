import time
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
