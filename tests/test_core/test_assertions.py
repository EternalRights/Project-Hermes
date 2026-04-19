from unittest.mock import MagicMock

import pytest

from hermes_core.assertions.engine import AssertionEngine, AssertionResult


@pytest.fixture
def engine():
    return AssertionEngine()


@pytest.fixture
def mock_response():
    resp = MagicMock()
    resp.status_code = 200
    resp.elapsed = 50
    resp.text = '{"code": 200, "message": "success", "data": {"id": 1, "name": "hermes", "tags": ["api", "test"]}}'
    resp.json.return_value = {
        "code": 200,
        "message": "success",
        "data": {"id": 1, "name": "hermes", "tags": ["api", "test"]},
    }
    return resp


def test_assert_status_code_pass(engine):
    result = engine.assert_status_code(200, 200)
    assert result.passed is True
    assert result.assertion_type == "status_code"
    assert result.expected == 200
    assert result.actual == 200
    assert result.message == ""


def test_assert_status_code_fail(engine):
    result = engine.assert_status_code(404, 200)
    assert result.passed is False
    assert result.assertion_type == "status_code"
    assert result.expected == 200
    assert result.actual == 404
    assert "Expected status 200" in result.message


def test_assert_json_path_eq(engine, mock_response):
    result = engine.assert_json_path(mock_response, "$.data.name", "hermes", "eq")
    assert result.passed is True
    assert result.assertion_type == "json_path"
    assert result.actual == "hermes"


def test_assert_json_path_contains(engine, mock_response):
    result = engine.assert_json_path(mock_response, "$.data.name", "herm", "contains")
    assert result.passed is True
    assert result.assertion_type == "json_path"


def test_assert_regex_match(engine):
    result = engine.assert_regex("hello world 123", r"\d+", True)
    assert result.passed is True
    assert result.assertion_type == "regex"
    assert result.actual is True


def test_assert_response_time_pass(engine):
    result = engine.assert_response_time(50, 100)
    assert result.passed is True
    assert result.assertion_type == "response_time"
    assert result.expected == "<=100ms"


def test_assert_response_time_fail(engine):
    result = engine.assert_response_time(200, 100)
    assert result.passed is False
    assert result.assertion_type == "response_time"
    assert "exceeded" in result.message


def test_assert_schema_valid(engine):
    schema = {
        "type": "object",
        "properties": {
            "code": {"type": "integer"},
            "message": {"type": "string"},
        },
        "required": ["code", "message"],
    }
    data = {"code": 200, "message": "success"}
    result = engine.assert_schema(data, schema)
    assert result.passed is True
    assert result.assertion_type == "schema"


def test_assert_schema_invalid(engine):
    schema = {
        "type": "object",
        "properties": {
            "code": {"type": "integer"},
        },
        "required": ["code"],
    }
    data = {"code": "not_an_integer"}
    result = engine.assert_schema(data, schema)
    assert result.passed is False
    assert result.assertion_type == "schema"
    assert result.actual == "invalid"


def test_run_assertions(engine, mock_response):
    config = [
        {"type": "status_code", "expected": 200},
        {"type": "json_path", "path": "$.data.name", "expected": "hermes", "comparison": "eq"},
        {"type": "regex", "pattern": r"hermes"},
        {"type": "response_time", "max_ms": 100},
        {"type": "schema", "schema": {"type": "object", "properties": {"code": {"type": "integer"}}, "required": ["code"]}},
    ]
    results = engine.run_assertions(mock_response, config)
    assert len(results) == 5
    assert all(r.passed for r in results)
