from unittest.mock import MagicMock, patch

import pytest

from hermes_core.executor.runner import TestCaseResult, _Context, _render_template, _render_value, TestCaseRunner
from hermes_core.executor.http_client import HttpResponse
from hermes_core.executor.retry import RetryPolicy


class TestTestCaseResult:

    def test_init_defaults(self):
        result = TestCaseResult(status="pass")
        assert result.status == "pass"
        assert result.response is None
        assert result.assertion_results == []
        assert result.extracted_variables == {}
        assert result.duration == 0.0
        assert result.error_message == ""

    def test_init_with_all_params(self):
        resp = HttpResponse(status_code=200, headers={}, body=b"ok", elapsed=10.0)
        assertion_results = [MagicMock(passed=True)]
        extracted = {"token": "abc"}
        result = TestCaseResult(
            status="pass",
            response=resp,
            assertion_results=assertion_results,
            extracted_variables=extracted,
            duration=50.0,
            error_message="",
        )
        assert result.status == "pass"
        assert result.response is resp
        assert result.assertion_results == assertion_results
        assert result.extracted_variables == extracted
        assert result.duration == 50.0

    def test_repr(self):
        result = TestCaseResult(status="pass", duration=123.45)
        assert repr(result) == "TestCaseResult(status=pass, duration=123.45ms)"


class TestContext:

    def test_init_defaults(self):
        ctx = _Context()
        assert ctx.variables == {}
        assert ctx.errors == []

    def test_init_with_variables(self):
        ctx = _Context(variables={"key": "val"})
        assert ctx.variables == {"key": "val"}


class TestRenderTemplate:

    def test_with_matching_variables(self):
        result = _render_template("Hello ${name}!", {"name": "World"})
        assert result == "Hello World!"

    def test_with_multiple_variables(self):
        result = _render_template("${host}:${port}", {"host": "localhost", "port": "8080"})
        assert result == "localhost:8080"

    def test_with_missing_variables(self):
        result = _render_template("Hello ${name}!", {})
        assert result == "Hello ${name}!"

    def test_with_non_string_input(self):
        assert _render_template(123, {}) == 123
        assert _render_template(None, {}) is None
        assert _render_template([1, 2], {}) == [1, 2]

    def test_with_no_placeholders(self):
        result = _render_template("plain text", {"key": "val"})
        assert result == "plain text"

    def test_variable_converted_to_str(self):
        result = _render_template("count: ${count}", {"count": 42})
        assert result == "count: 42"


class TestRenderValue:

    def test_string_value(self):
        result = _render_value("${name}", {"name": "test"})
        assert result == "test"

    def test_dict_value(self):
        value = {"url": "${host}/api", "method": "GET"}
        result = _render_value(value, {"host": "http://example.com"})
        assert result == {"url": "http://example.com/api", "method": "GET"}

    def test_list_value(self):
        value = ["${a}", "${b}"]
        result = _render_value(value, {"a": "1", "b": "2"})
        assert result == ["1", "2"]

    def test_other_types(self):
        assert _render_value(123, {}) == 123
        assert _render_value(3.14, {}) == 3.14
        assert _render_value(True, {}) is True
        assert _render_value(None, {}) is None

    def test_nested_dict_and_list(self):
        value = {"headers": ["${token}"], "body": {"key": "${val}"}}
        result = _render_value(value, {"token": "abc", "val": "xyz"})
        assert result == {"headers": ["abc"], "body": {"key": "xyz"}}


class TestTestCaseRunner:

    def _make_response(self, status_code=200, body=None):
        if body is None:
            body = b'{"result": true}'
        return HttpResponse(status_code=status_code, headers={}, body=body, elapsed=50.0)

    def test_run_full_execution_flow(self):
        mock_http_client = MagicMock()
        mock_http_client.send.return_value = self._make_response()

        mock_assertion_engine = MagicMock()
        mock_assertion_result = MagicMock()
        mock_assertion_result.passed = True
        mock_assertion_engine.run_assertions.return_value = [mock_assertion_result]

        mock_extractor = MagicMock()
        mock_extractor.extract_variables.return_value = {"token": "abc123"}

        mock_hook_executor = MagicMock()
        mock_hook_executor.execute_pre_hooks.side_effect = lambda hooks, ctx: ctx
        mock_hook_executor.execute_post_hooks.side_effect = lambda hooks, ctx, resp: ctx

        runner = TestCaseRunner(http_client=mock_http_client)
        runner.assertion_engine = mock_assertion_engine
        runner.variable_extractor = mock_extractor
        runner.hook_executor = mock_hook_executor

        case_config = {
            "variables": {"host": "http://example.com"},
            "request": {
                "method": "GET",
                "url": "${host}/api",
                "headers": {"Authorization": "Bearer token"},
            },
            "assertions": [{"type": "status_code", "expected": 200}],
            "extract": [{"type": "json_path", "path": "$.token", "variable": "token"}],
            "pre_hooks": [{"type": "script", "content": "pass"}],
            "post_hooks": [{"type": "script", "content": "pass"}],
        }

        result = runner.run(case_config)

        assert result.status == "pass"
        assert result.response.status_code == 200
        assert result.extracted_variables == {"token": "abc123"}
        assert result.error_message == ""
        mock_http_client.send.assert_called_once()
        mock_hook_executor.execute_pre_hooks.assert_called_once()
        mock_hook_executor.execute_post_hooks.assert_called_once()
        mock_extractor.extract_variables.assert_called_once()

    def test_run_with_failed_assertion(self):
        mock_http_client = MagicMock()
        mock_http_client.send.return_value = self._make_response(status_code=500)

        mock_assertion_engine = MagicMock()
        mock_pass = MagicMock()
        mock_pass.passed = True
        mock_fail = MagicMock()
        mock_fail.passed = False
        mock_assertion_engine.run_assertions.return_value = [mock_pass, mock_fail]

        mock_extractor = MagicMock()
        mock_extractor.extract_variables.return_value = {}

        mock_hook_executor = MagicMock()
        mock_hook_executor.execute_pre_hooks.side_effect = lambda hooks, ctx: ctx
        mock_hook_executor.execute_post_hooks.side_effect = lambda hooks, ctx, resp: ctx

        runner = TestCaseRunner(http_client=mock_http_client)
        runner.assertion_engine = mock_assertion_engine
        runner.variable_extractor = mock_extractor
        runner.hook_executor = mock_hook_executor

        case_config = {
            "request": {"method": "GET", "url": "http://example.com"},
            "assertions": [{"type": "status_code", "expected": 200}],
        }

        result = runner.run(case_config)
        assert result.status == "fail"

    def test_run_with_retry_policy(self):
        mock_http_client = MagicMock()
        mock_http_client.send.return_value = self._make_response()

        mock_assertion_engine = MagicMock()
        mock_assertion_engine.run_assertions.return_value = []

        mock_extractor = MagicMock()
        mock_extractor.extract_variables.return_value = {}

        mock_hook_executor = MagicMock()
        mock_hook_executor.execute_pre_hooks.side_effect = lambda hooks, ctx: ctx
        mock_hook_executor.execute_post_hooks.side_effect = lambda hooks, ctx, resp: ctx

        retry_policy = RetryPolicy(max_retries=2, retry_interval=0.01)

        runner = TestCaseRunner(http_client=mock_http_client, retry_policy=retry_policy)
        runner.assertion_engine = mock_assertion_engine
        runner.variable_extractor = mock_extractor
        runner.hook_executor = mock_hook_executor

        case_config = {
            "request": {"method": "GET", "url": "http://example.com"},
        }

        with patch("hermes_core.executor.retry.time.sleep"):
            result = runner.run(case_config)

        assert result.status == "pass"

    def test_run_with_exception_during_execution(self):
        mock_http_client = MagicMock()
        mock_http_client.send.side_effect = ConnectionError("connection refused")

        runner = TestCaseRunner(http_client=mock_http_client)

        case_config = {
            "request": {"method": "GET", "url": "http://example.com"},
        }

        result = runner.run(case_config)
        assert result.status == "error"
        assert "connection refused" in result.error_message
        assert result.duration > 0

    def test_run_variable_merging(self):
        mock_http_client = MagicMock()
        mock_http_client.send.return_value = self._make_response()

        mock_assertion_engine = MagicMock()
        mock_assertion_engine.run_assertions.return_value = []

        mock_extractor = MagicMock()
        mock_extractor.extract_variables.return_value = {}

        mock_hook_executor = MagicMock()
        mock_hook_executor.execute_pre_hooks.side_effect = lambda hooks, ctx: ctx
        mock_hook_executor.execute_post_hooks.side_effect = lambda hooks, ctx, resp: ctx

        runner = TestCaseRunner(http_client=mock_http_client)
        runner.assertion_engine = mock_assertion_engine
        runner.variable_extractor = mock_extractor
        runner.hook_executor = mock_hook_executor

        case_config = {
            "variables": {"host": "http://global.com", "shared": "global"},
            "env_variables": {"env": "prod", "shared": "env"},
            "case_variables": {"case": "specific"},
            "request": {"method": "GET", "url": "${host}"},
        }

        result = runner.run(case_config, variables={"param": "override"})

        assert result.status == "pass"
        call_args = mock_http_client.send.call_args
        assert call_args[0][1] == "http://global.com"

    def test_run_param_vars_override_case_vars(self):
        mock_http_client = MagicMock()
        mock_http_client.send.return_value = self._make_response()

        mock_assertion_engine = MagicMock()
        mock_assertion_engine.run_assertions.return_value = []

        mock_extractor = MagicMock()
        mock_extractor.extract_variables.return_value = {}

        mock_hook_executor = MagicMock()
        mock_hook_executor.execute_pre_hooks.side_effect = lambda hooks, ctx: ctx
        mock_hook_executor.execute_post_hooks.side_effect = lambda hooks, ctx, resp: ctx

        runner = TestCaseRunner(http_client=mock_http_client)
        runner.assertion_engine = mock_assertion_engine
        runner.variable_extractor = mock_extractor
        runner.hook_executor = mock_hook_executor

        case_config = {
            "case_variables": {"key": "case_val"},
            "request": {"method": "GET", "url": "http://example.com/${key}"},
        }

        result = runner.run(case_config, variables={"key": "param_val"})

        call_args = mock_http_client.send.call_args
        assert call_args[0][1] == "http://example.com/param_val"

    def test_run_empty_case_config(self):
        mock_http_client = MagicMock()
        mock_http_client.send.return_value = self._make_response()

        mock_assertion_engine = MagicMock()
        mock_assertion_engine.run_assertions.return_value = []

        mock_extractor = MagicMock()
        mock_extractor.extract_variables.return_value = {}

        mock_hook_executor = MagicMock()
        mock_hook_executor.execute_pre_hooks.side_effect = lambda hooks, ctx: ctx
        mock_hook_executor.execute_post_hooks.side_effect = lambda hooks, ctx, resp: ctx

        runner = TestCaseRunner(http_client=mock_http_client)
        runner.assertion_engine = mock_assertion_engine
        runner.variable_extractor = mock_extractor
        runner.hook_executor = mock_hook_executor

        result = runner.run({})

        assert result.status == "pass"
        mock_http_client.send.assert_called_once_with("GET", "", headers=None, params=None, body=None, json=None, files=None)

    def test_run_default_method_is_get(self):
        mock_http_client = MagicMock()
        mock_http_client.send.return_value = self._make_response()

        mock_assertion_engine = MagicMock()
        mock_assertion_engine.run_assertions.return_value = []

        mock_extractor = MagicMock()
        mock_extractor.extract_variables.return_value = {}

        mock_hook_executor = MagicMock()
        mock_hook_executor.execute_pre_hooks.side_effect = lambda hooks, ctx: ctx
        mock_hook_executor.execute_post_hooks.side_effect = lambda hooks, ctx, resp: ctx

        runner = TestCaseRunner(http_client=mock_http_client)
        runner.assertion_engine = mock_assertion_engine
        runner.variable_extractor = mock_extractor
        runner.hook_executor = mock_hook_executor

        case_config = {"request": {"url": "http://example.com"}}

        result = runner.run(case_config)

        call_args = mock_http_client.send.call_args
        assert call_args[0][0] == "GET"

    def test_run_post_method_with_json_body(self):
        mock_http_client = MagicMock()
        mock_http_client.send.return_value = self._make_response()

        mock_assertion_engine = MagicMock()
        mock_assertion_engine.run_assertions.return_value = []

        mock_extractor = MagicMock()
        mock_extractor.extract_variables.return_value = {}

        mock_hook_executor = MagicMock()
        mock_hook_executor.execute_pre_hooks.side_effect = lambda hooks, ctx: ctx
        mock_hook_executor.execute_post_hooks.side_effect = lambda hooks, ctx, resp: ctx

        runner = TestCaseRunner(http_client=mock_http_client)
        runner.assertion_engine = mock_assertion_engine
        runner.variable_extractor = mock_extractor
        runner.hook_executor = mock_hook_executor

        case_config = {
            "request": {
                "method": "POST",
                "url": "http://example.com/api",
                "json": {"name": "test"},
            },
        }

        result = runner.run(case_config)

        call_args = mock_http_client.send.call_args
        assert call_args[0][0] == "POST"
        assert call_args[1]["json"] == {"name": "test"}
