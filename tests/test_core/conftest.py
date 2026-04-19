from unittest.mock import MagicMock

import pytest

from hermes_core.executor.http_client import HttpClient, HttpResponse
from hermes_core.executor.runner import TestCaseResult


@pytest.fixture()
def mock_http_client():
    client = MagicMock(spec=HttpClient)
    client.timeout = 30
    client.verify_ssl = True
    client.proxies = None
    return client


@pytest.fixture()
def mock_response():
    return HttpResponse(
        status_code=200,
        headers={"Content-Type": "application/json"},
        body=b'{"code": 200, "message": "success", "data": {"id": 1, "name": "hermes"}}',
        elapsed=45.5,
        encoding="utf-8",
    )


@pytest.fixture()
def mock_error_response():
    return HttpResponse(
        status_code=500,
        headers={"Content-Type": "text/plain"},
        body=b"Internal Server Error",
        elapsed=1200.0,
        encoding="utf-8",
    )


@pytest.fixture()
def sample_case_config():
    return {
        "request": {
            "method": "POST",
            "url": "http://localhost:5000/api/v1/auth/login",
            "headers": {"Content-Type": "application/json", "Accept": "application/json"},
            "json": {"username": "admin", "password": "secret"},
        },
        "assertions": [
            {"type": "status_code", "expected": 200},
            {"type": "json_path", "path": "$.code", "expected": 200, "comparison": "eq"},
            {"type": "json_path", "path": "$.data.access_token", "expected": None, "comparison": "neq"},
            {"type": "response_time", "max_ms": 500},
        ],
        "extract": [
            {"type": "json_path", "path": "$.data.access_token", "variable": "auth_token"},
            {"type": "regex", "pattern": r"token", "variable": "token_found"},
        ],
        "pre_hooks": [
            {"type": "script", "content": "context.variables['timestamp'] = str(int(time.time()))"},
        ],
        "post_hooks": [
            {"type": "script", "content": "context.variables['status'] = str(response.status_code)"},
        ],
        "variables": {"base_url": "http://localhost:5000"},
    }


@pytest.fixture()
def sample_test_case_result():
    return TestCaseResult(
        status="pass",
        response=HttpResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body=b'{"code": 200, "message": "success"}',
            elapsed=45.5,
        ),
        assertion_results=[],
        extracted_variables={"auth_token": "jwt-token-value"},
        duration=45.5,
    )


@pytest.fixture()
def sample_failed_test_case_result():
    return TestCaseResult(
        status="fail",
        response=HttpResponse(
            status_code=500,
            headers={"Content-Type": "application/json"},
            body=b'{"code": 500, "message": "error"}',
            elapsed=1200.0,
        ),
        assertion_results=[],
        extracted_variables={},
        duration=1200.0,
        error_message="",
    )


@pytest.fixture()
def sample_error_test_case_result():
    return TestCaseResult(
        status="error",
        duration=0.0,
        error_message="Connection refused",
    )
