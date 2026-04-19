import pytest


@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:5000"


@pytest.fixture(scope="session")
def api_prefix():
    return "/api/v1"


@pytest.fixture(scope="session")
def test_headers():
    return {"Content-Type": "application/json"}
