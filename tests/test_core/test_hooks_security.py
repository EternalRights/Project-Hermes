import pytest
from unittest.mock import MagicMock
from hermes_core.executor.hooks import HookExecutor, _validate_script


class TestHookScriptValidation:
    def test_validate_simple_script(self):
        _validate_script("context.variables['x'] = 1")

    def test_validate_rejects_import(self):
        with pytest.raises(ValueError, match="Forbidden AST node"):
            _validate_script("import os")

    def test_validate_rejects_import_from(self):
        with pytest.raises(ValueError, match="Forbidden AST node"):
            _validate_script("from os import path")

    def test_validate_rejects_dunder_globals(self):
        with pytest.raises(ValueError, match="dangerous attribute"):
            _validate_script("x.__globals__")

    def test_validate_rejects_dunder_code(self):
        with pytest.raises(ValueError, match="dangerous attribute"):
            _validate_script("func.__code__")

    def test_validate_rejects_dunder_class(self):
        with pytest.raises(ValueError, match="dangerous attribute"):
            _validate_script("obj.__class__")


class TestHookExecutorTimeout:
    def test_script_timeout(self):
        executor = HookExecutor()
        context = MagicMock()
        context.errors = []

        long_running_script = """
i = 0
while i < 1000000000:
    i += 1
"""
        executor._run_script(long_running_script, {"context": context, "response": None}, timeout=1)
        assert any("timed out" in str(e).lower() for e in context.errors)

    def test_script_error_caught(self):
        executor = HookExecutor()
        context = MagicMock()
        context.errors = []

        error_script = "raise ValueError('test error')"
        executor._run_script(error_script, {"context": context, "response": None})
        assert any("test error" in str(e) for e in context.errors)
