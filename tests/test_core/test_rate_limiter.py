import time
from concurrent.futures import ThreadPoolExecutor

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


def test_rate_limiter_wait():
    limiter = TokenBucketRateLimiter(rate=1000, capacity=1)
    limiter.acquire()
    wait_time = limiter.wait(1)
    assert wait_time >= 0


def test_rate_limiter_concurrent_acquire():
    limiter = TokenBucketRateLimiter(rate=1, capacity=10)
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(limiter.acquire) for _ in range(20)]
        results = [f.result() for f in futures]
    acquired = sum(1 for r in results if r is True)
    assert acquired <= 12


def test_rate_limiter_acquire_with_tokens():
    limiter = TokenBucketRateLimiter(rate=1, capacity=5)
    assert limiter.acquire(tokens=2) is True
    assert limiter.acquire(tokens=2) is True
    assert limiter.acquire(tokens=2) is False
