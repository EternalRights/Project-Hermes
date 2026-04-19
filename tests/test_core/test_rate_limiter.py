import time

from hermes_core.utils.rate_limiter import TokenBucketRateLimiter

import pytest


def test_rate_limiter_acquire():
    limiter = TokenBucketRateLimiter(rate=10, capacity=5)
    for _ in range(5):
        assert limiter.acquire() is True


def test_rate_limiter_acquire_exhaust():
    limiter = TokenBucketRateLimiter(rate=1, capacity=2)
    assert limiter.acquire() is True
    assert limiter.acquire() is True
    assert limiter.acquire() is False
