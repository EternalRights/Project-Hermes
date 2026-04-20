from unittest.mock import MagicMock

from hermes_core.executor.runner import TestCaseRunner, TestCaseResult, _render_template, _render_value, _Context
from hermes_core.executor.http_client import HttpResponse
from hermes_core.executor.extractor import VariableExtractor
from hermes_core.executor.hooks import HookExecutor
from hermes_core.assertions.engine import AssertionEngine
from hermes_core.parametrize.scope import VariableScope
from hermes_core.parametrize.template import TemplateRenderer


class TestFullExecutionPipeline:
    def test_full_pipeline_pass(self):
        mock_client = MagicMock()
        mock_response = HttpResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body='{"code": 200, "data": {"token": "abc123", "user_id": 42}}',
            elapsed=50.0,
        )
        mock_client.send.return_value = mock_response

        runner = TestCaseRunner(http_client=mock_client)

        case_config = {
            "request": {
                "method": "POST",
                "url": "http://localhost:5000/api/login",
                "headers": {"Content-Type": "application/json"},
                "json": {"username": "admin", "password": "123456"},
            },
            "assertions": [
                {"type": "status_code", "expected": 200},
                {"type": "json_path", "path": "$.code", "expected": 200, "comparison": "eq"},
                {"type": "response_time", "max_ms": 1000},
            ],
            "extract": [
                {"type": "json_path", "path": "$.data.token", "variable": "auth_token"},
                {"type": "regex", "pattern": r"user_id\": (\d+)", "variable": "uid", "group": 1},
            ],
            "variables": {"base_url": "http://localhost:5000"},
        }

        result = runner.run(case_config)
        assert result.status == "pass"
        assert result.duration > 0
        assert len(result.assertion_results) == 3
        assert all(r.passed for r in result.assertion_results)
        assert result.extracted_variables.get("auth_token") == "abc123"
        assert result.extracted_variables.get("uid") == "42"

    def test_full_pipeline_fail_assertion(self):
        mock_client = MagicMock()
        mock_response = HttpResponse(
            status_code=500,
            headers={},
            body='{"error": "internal"}',
            elapsed=200.0,
        )
        mock_client.send.return_value = mock_response

        runner = TestCaseRunner(http_client=mock_client)
        case_config = {
            "request": {"method": "GET", "url": "http://localhost/error"},
            "assertions": [{"type": "status_code", "expected": 200}],
        }
        result = runner.run(case_config)
        assert result.status == "fail"

    def test_full_pipeline_exception(self):
        mock_client = MagicMock()
        mock_client.send.side_effect = ConnectionError("Connection refused")

        runner = TestCaseRunner(http_client=mock_client)
        case_config = {
            "request": {"method": "GET", "url": "http://unreachable/"},
            "assertions": [],
        }
        result = runner.run(case_config)
        assert result.status == "error"
        assert "Connection refused" in result.error_message

    def test_pipeline_with_pre_hooks_setting_variables(self):
        mock_client = MagicMock()
        mock_response = HttpResponse(status_code=200, headers={}, body="{}", elapsed=10.0)
        mock_client.send.return_value = mock_response

        runner = TestCaseRunner(http_client=mock_client)
        case_config = {
            "request": {"method": "GET", "url": "http://localhost/test"},
            "assertions": [],
            "pre_hooks": [
                {"type": "script", "content": "context.variables['dynamic_key'] = 'dynamic_value'"},
            ],
        }
        result = runner.run(case_config)
        assert result.status == "pass"

    def test_pipeline_with_post_hooks_accessing_response(self):
        mock_client = MagicMock()
        mock_response = HttpResponse(
            status_code=200,
            headers={},
            body='{"status": "ok"}',
            elapsed=10.0,
        )
        mock_client.send.return_value = mock_response

        runner = TestCaseRunner(http_client=mock_client)
        case_config = {
            "request": {"method": "GET", "url": "http://localhost/test"},
            "assertions": [],
            "post_hooks": [
                {"type": "script", "content": "context.variables['resp_status'] = response.status_code"},
            ],
        }
        result = runner.run(case_config)
        assert result.status == "pass"


class TestMultiStepVariablePassing:
    def test_variable_extraction_and_reuse(self):
        extractor = VariableExtractor()
        scope = VariableScope()
        renderer = TemplateRenderer()

        scope.set_environment("base_url", "http://localhost:5000")

        step1_response = HttpResponse(
            status_code=200,
            headers={},
            body='{"token": "secret_jwt_token", "user_id": 100}',
            elapsed=30.0,
        )

        extracted = extractor.extract_variables(step1_response, [
            {"type": "json_path", "path": "$.token", "variable": "auth_token"},
            {"type": "json_path", "path": "$.user_id", "variable": "user_id"},
        ])
        assert extracted["auth_token"] == "secret_jwt_token"
        assert extracted["user_id"] == 100

        for k, v in extracted.items():
            scope.set_step(k, v)

        merged = scope.merge()
        url_template = "{{base_url}}/api/users/{{user_id}}"
        rendered_url = renderer.render(url_template, merged)
        assert rendered_url == "http://localhost:5000/api/users/100"

        header_template = "Bearer {{auth_token}}"
        rendered_header = renderer.render(header_template, merged)
        assert rendered_header == "Bearer secret_jwt_token"

    def test_variable_scope_clearing_between_cases(self):
        scope = VariableScope()
        scope.set_global("g_key", "global_val")
        scope.set_environment("e_key", "env_val")

        scope.set_case("case1_var", "case1_val")
        scope.set_step("step1_var", "step1_val")

        scope.clear_scope(VariableScope.SCOPE_STEP)
        scope.clear_scope(VariableScope.SCOPE_CASE)

        assert scope.get("g_key") == "global_val"
        assert scope.get("e_key") == "env_val"

    def test_template_rendering_with_extracted_variables(self):
        renderer = TemplateRenderer()
        variables = {
            "base_url": "http://api.example.com",
            "token": "jwt_abc123",
            "user_id": "42",
        }

        data = {
            "url": "{{base_url}}/users/{{user_id}}",
            "headers": {"Authorization": "Bearer {{token}}"},
            "body": {"id": "{{user_id}}"},
        }

        rendered = renderer.render_dict(data, variables)
        assert rendered["url"] == "http://api.example.com/users/42"
        assert rendered["headers"]["Authorization"] == "Bearer jwt_abc123"
        assert rendered["body"]["id"] == "42"
