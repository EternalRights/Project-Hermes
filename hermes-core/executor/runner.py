import re
import time

from .http_client import HttpClient
from .retry import RetryPolicy, RetryableHttpClient
from .extractor import VariableExtractor
from .hooks import HookExecutor
from assertions.engine import AssertionEngine


class TestCaseResult:

    def __init__(self, status, response=None, assertion_results=None,
                 extracted_variables=None, duration=0.0, error_message=""):
        self.status = status
        self.response = response
        self.assertion_results = assertion_results if assertion_results is not None else []
        self.extracted_variables = extracted_variables if extracted_variables is not None else {}
        self.duration = duration
        self.error_message = error_message

    def __repr__(self):
        return f"TestCaseResult(status={self.status}, duration={self.duration}ms)"


class _Context:

    def __init__(self, variables=None):
        self.variables = variables if variables is not None else {}
        self.errors = []


def _render_template(text, variables):
    if not isinstance(text, str):
        return text

    def _replace(match):
        key = match.group(1)
        return str(variables.get(key, match.group(0)))

    return re.sub(r"\$\{(\w+)\}", _replace, text)


def _render_value(value, variables):
    if isinstance(value, str):
        return _render_template(value, variables)
    if isinstance(value, dict):
        return {k: _render_value(v, variables) for k, v in value.items()}
    if isinstance(value, list):
        return [_render_value(item, variables) for item in value]
    return value


class TestCaseRunner:

    def __init__(self, http_client=None, retry_policy=None):
        self.http_client = http_client or HttpClient()
        self.retry_policy = retry_policy
        self.assertion_engine = AssertionEngine()
        self.variable_extractor = VariableExtractor()
        self.hook_executor = HookExecutor()

    def run(self, case_config, variables=None):
        start_time = time.time()
        try:
            merged_vars = {}
            global_vars = case_config.get("variables", {})
            env_vars = case_config.get("env_variables", {})
            case_vars = case_config.get("case_variables", {})
            param_vars = variables or {}
            merged_vars.update(global_vars)
            merged_vars.update(env_vars)
            merged_vars.update(case_vars)
            merged_vars.update(param_vars)

            context = _Context(variables=merged_vars)

            pre_hooks = case_config.get("pre_hooks", [])
            context = self.hook_executor.execute_pre_hooks(pre_hooks, context)

            request_cfg = case_config.get("request", {})
            rendered_cfg = _render_value(request_cfg, context.variables)

            method = rendered_cfg.get("method", "GET")
            url = rendered_cfg.get("url", "")
            headers = rendered_cfg.get("headers")
            params = rendered_cfg.get("params")
            body = rendered_cfg.get("body")
            json_body = rendered_cfg.get("json")
            files = rendered_cfg.get("files")

            if self.retry_policy:
                client = RetryableHttpClient(self.http_client, self.retry_policy)
                response = client.send_with_retry(method, url, headers=headers,
                                                  params=params, body=body,
                                                  json=json_body, files=files)
            else:
                response = self.http_client.send(method, url, headers=headers,
                                                 params=params, body=body,
                                                 json=json_body, files=files)

            assertions_config = case_config.get("assertions", [])
            assertion_results = self.assertion_engine.run_assertions(response, assertions_config)

            extract_config = case_config.get("extract", [])
            extracted = self.variable_extractor.extract_variables(response, extract_config)
            context.variables.update(extracted)

            post_hooks = case_config.get("post_hooks", [])
            context = self.hook_executor.execute_post_hooks(post_hooks, context, response)

            elapsed = (time.time() - start_time) * 1000

            all_passed = all(r.passed for r in assertion_results)
            status = "pass" if all_passed else "fail"

            return TestCaseResult(
                status=status,
                response=response,
                assertion_results=assertion_results,
                extracted_variables=extracted,
                duration=elapsed,
            )
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            return TestCaseResult(
                status="error",
                duration=elapsed,
                error_message=str(e),
            )
