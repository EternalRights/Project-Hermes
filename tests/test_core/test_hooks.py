import time
from unittest.mock import MagicMock, patch

import pytest

from hermes_core.executor.hooks import HookExecutor


@pytest.fixture
def executor():
    return HookExecutor()


@pytest.fixture
def context():
    class _Ctx:
        def __init__(self):
            self.variables = {"base_url": "http://example.com"}
            self.errors = []
    return _Ctx()


@pytest.fixture
def mock_response():
    resp = MagicMock()
    resp.status_code = 200
    resp.text = "ok"
    resp.json.return_value = {"result": True}
    return resp


class TestExecutePreHooks:

    def test_script_hook_modifies_context(self, executor, context):
        hooks = [
            {"type": "script", "content": "context.variables['new_key'] = 'new_val'"},
        ]
        result = executor.execute_pre_hooks(hooks, context)
        assert result.variables["new_key"] == "new_val"

    @patch("hermes_core.executor.hooks.time.sleep")
    def test_wait_hook_calls_sleep(self, mock_sleep, executor, context):
        hooks = [
            {"type": "wait", "duration": 2},
        ]
        executor.execute_pre_hooks(hooks, context)
        mock_sleep.assert_called_once_with(2)

    @patch("hermes_core.executor.hooks.time.sleep")
    def test_wait_hook_default_duration(self, mock_sleep, executor, context):
        hooks = [
            {"type": "wait"},
        ]
        executor.execute_pre_hooks(hooks, context)
        mock_sleep.assert_called_once_with(1)

    def test_empty_hooks(self, executor, context):
        result = executor.execute_pre_hooks([], context)
        assert result is context

    def test_none_hooks(self, executor, context):
        result = executor.execute_pre_hooks(None, context)
        assert result is context

    def test_multiple_hooks(self, executor, context):
        hooks = [
            {"type": "script", "content": "context.variables['a'] = 1"},
            {"type": "script", "content": "context.variables['b'] = 2"},
        ]
        result = executor.execute_pre_hooks(hooks, context)
        assert result.variables["a"] == 1
        assert result.variables["b"] == 2

    def test_unknown_hook_type_ignored(self, executor, context):
        hooks = [
            {"type": "unknown_type", "some_key": "some_val"},
        ]
        result = executor.execute_pre_hooks(hooks, context)
        assert result is context


class TestExecutePostHooks:

    def test_script_hook_accesses_response(self, executor, context, mock_response):
        hooks = [
            {"type": "script", "content": "context.variables['status'] = response.status_code"},
        ]
        result = executor.execute_post_hooks(hooks, context, mock_response)
        assert result.variables["status"] == 200

    def test_script_hook_accesses_response_json(self, executor, context, mock_response):
        hooks = [
            {"type": "script", "content": "context.variables['result'] = response.json()['result']"},
        ]
        result = executor.execute_post_hooks(hooks, context, mock_response)
        assert result.variables["result"] is True

    @patch("hermes_core.executor.hooks.time.sleep")
    def test_wait_hook_in_post(self, mock_sleep, executor, context, mock_response):
        hooks = [
            {"type": "wait", "duration": 3},
        ]
        executor.execute_post_hooks(hooks, context, mock_response)
        mock_sleep.assert_called_once_with(3)

    def test_empty_hooks(self, executor, context, mock_response):
        result = executor.execute_post_hooks([], context, mock_response)
        assert result is context

    def test_none_hooks(self, executor, context, mock_response):
        result = executor.execute_post_hooks(None, context, mock_response)
        assert result is context


class TestRunScriptErrorHandling:

    def test_script_exception_appended_to_errors(self, executor, context):
        hooks = [
            {"type": "script", "content": "x = 1 / 0"},
        ]
        executor.execute_pre_hooks(hooks, context)
        assert len(context.errors) == 1
        assert "division by zero" in context.errors[0]

    def test_script_exception_in_post_hooks(self, executor, context, mock_response):
        hooks = [
            {"type": "script", "content": "x = 1 / 0"},
        ]
        executor.execute_post_hooks(hooks, context, mock_response)
        assert len(context.errors) == 1
        assert "division by zero" in context.errors[0]

    def test_multiple_errors_accumulated(self, executor, context):
        hooks = [
            {"type": "script", "content": "x = 1 / 0"},
            {"type": "script", "content": "int('not_a_number')"},
        ]
        executor.execute_pre_hooks(hooks, context)
        assert len(context.errors) == 2

    def test_error_does_not_stop_subsequent_hooks(self, executor, context):
        hooks = [
            {"type": "script", "content": "raise ValueError('error1')"},
            {"type": "script", "content": "context.variables['after_error'] = True"},
        ]
        executor.execute_pre_hooks(hooks, context)
        assert context.variables["after_error"] is True


class TestRunScriptSafeGlobals:

    def test_safe_builtins_available(self, executor, context):
        hooks = [
            {"type": "script", "content": "context.variables['len_result'] = len([1, 2, 3])"},
        ]
        executor.execute_pre_hooks(hooks, context)
        assert context.variables["len_result"] == 3

    def test_dangerous_builtins_blocked(self, executor, context):
        hooks = [
            {"type": "script", "content": "context.variables['imp'] = __import__('os')"},
        ]
        executor.execute_pre_hooks(hooks, context)
        assert len(context.errors) == 1

    def test_open_not_available(self, executor, context):
        hooks = [
            {"type": "script", "content": "open('/etc/passwd', 'r')"},
        ]
        executor.execute_pre_hooks(hooks, context)
        assert len(context.errors) == 1

    def test_exec_not_available(self, executor, context):
        hooks = [
            {"type": "script", "content": "exec('x = 1')"},
        ]
        executor.execute_pre_hooks(hooks, context)
        assert len(context.errors) == 1

    def test_eval_not_available(self, executor, context):
        hooks = [
            {"type": "script", "content": "eval('1 + 1')"},
        ]
        executor.execute_pre_hooks(hooks, context)
        assert len(context.errors) == 1

    def test_time_module_available(self, executor, context):
        hooks = [
            {"type": "script", "content": "context.variables['time_mod'] = time.time() > 0"},
        ]
        executor.execute_pre_hooks(hooks, context)
        assert context.variables["time_mod"] is True

    def test_type_casting_available(self, executor, context):
        hooks = [
            {"type": "script", "content": "context.variables['val'] = int('42') + float('1.5')"},
        ]
        executor.execute_pre_hooks(hooks, context)
        assert context.variables["val"] == 43.5
