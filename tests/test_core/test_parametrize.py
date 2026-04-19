import hashlib
import re
import time
import uuid

from hermes_core.parametrize.functions import BuiltinFunctions, FUNCTIONS
from hermes_core.parametrize.scope import VariableScope
from hermes_core.parametrize.template import TemplateRenderer

import pytest


@pytest.fixture
def scope():
    return VariableScope()


@pytest.fixture
def renderer():
    return TemplateRenderer()


def test_variable_scope_set_get(scope):
    scope.set_global("g_key", "global_val")
    scope.set_environment("e_key", "env_val")
    scope.set_case("c_key", "case_val")
    scope.set_step("s_key", "step_val")
    assert scope.get("g_key") == "global_val"
    assert scope.get("e_key") == "env_val"
    assert scope.get("c_key") == "case_val"
    assert scope.get("s_key") == "step_val"


def test_variable_scope_priority(scope):
    scope.set_global("key", "global")
    scope.set_environment("key", "environment")
    scope.set_case("key", "case")
    scope.set_step("key", "step")
    assert scope.get("key") == "step"
    scope.clear_scope(VariableScope.SCOPE_STEP)
    assert scope.get("key") == "case"
    scope.clear_scope(VariableScope.SCOPE_CASE)
    assert scope.get("key") == "environment"
    scope.clear_scope(VariableScope.SCOPE_ENVIRONMENT)
    assert scope.get("key") == "global"


def test_variable_scope_merge(scope):
    scope.set_global("a", 1)
    scope.set_global("b", 2)
    scope.set_environment("b", 20)
    scope.set_environment("c", 30)
    scope.set_case("d", 40)
    scope.set_step("e", 50)
    merged = scope.merge()
    assert merged["a"] == 1
    assert merged["b"] == 20
    assert merged["c"] == 30
    assert merged["d"] == 40
    assert merged["e"] == 50


def test_template_render_variable(renderer):
    template = "Hello, {{name}}! Welcome to {{project}}."
    variables = {"name": "Hermes", "project": "API Testing"}
    result = renderer.render(template, variables)
    assert result == "Hello, Hermes! Welcome to API Testing."


def test_template_render_function(renderer):
    template = "{{random_int(1, 100)}}"
    result = renderer.render(template, {})
    assert result.isdigit()
    val = int(result)
    assert 1 <= val <= 100


def test_template_render_dict(renderer):
    data = {
        "url": "{{base_url}}/api/v1",
        "headers": {
            "Authorization": "Bearer {{token}}",
        },
        "body": ["{{item1}}", "{{item2}}"],
    }
    variables = {"base_url": "http://localhost", "token": "abc123", "item1": "foo", "item2": "bar"}
    result = renderer.render_dict(data, variables)
    assert result["url"] == "http://localhost/api/v1"
    assert result["headers"]["Authorization"] == "Bearer abc123"
    assert result["body"] == ["foo", "bar"]


def test_builtin_functions_random_int():
    val = BuiltinFunctions.random_int(1, 10)
    assert isinstance(val, int)
    assert 1 <= val <= 10


def test_builtin_functions_uuid():
    val = BuiltinFunctions.uuid()
    assert isinstance(val, str)
    parsed = uuid.UUID(val)
    assert str(parsed) == val


def test_builtin_functions_md5():
    val = BuiltinFunctions.md5("hello")
    expected = hashlib.md5(b"hello").hexdigest()
    assert val == expected


def test_builtin_functions_timestamp():
    before = int(time.time())
    val = BuiltinFunctions.timestamp()
    after = int(time.time())
    assert before <= val <= after


def test_builtin_functions_random_string():
    val = BuiltinFunctions.random_string(16)
    assert isinstance(val, str)
    assert len(val) == 16
    import string as string_mod
    allowed = set(string_mod.ascii_letters + string_mod.digits)
    assert all(c in allowed for c in val)


def test_builtin_functions_hmac_sha256():
    val = BuiltinFunctions.hmac_sha256("secret", "message")
    assert isinstance(val, str)
    assert len(val) == 64
    try:
        int(val, 16)
    except ValueError:
        pytest.fail("hmac_sha256 output is not a valid hex string")


def test_builtin_functions_base64_encode():
    val = BuiltinFunctions.base64_encode("hello")
    assert isinstance(val, str)
    import base64
    assert val == base64.b64encode(b"hello").decode("utf-8")


def test_builtin_functions_base64_decode():
    encoded = BuiltinFunctions.base64_encode("test data")
    decoded = BuiltinFunctions.base64_decode(encoded)
    assert decoded == "test data"


def test_builtin_functions_date_format():
    val = BuiltinFunctions.date_format("%Y-%m-%d")
    assert isinstance(val, str)
    import re as re_mod
    assert re_mod.match(r"\d{4}-\d{2}-\d{2}", val)


def test_builtin_functions_now_iso():
    val = BuiltinFunctions.now_iso()
    assert isinstance(val, str)
    assert "T" in val


def test_template_render_unknown_function(renderer):
    with pytest.raises(ValueError, match="Unknown function"):
        renderer.render("{{nonexistent_func()}}", {})


def test_template_render_unresolved_variable(renderer):
    template = "Hello, {{unknown_var}}!"
    result = renderer.render(template, {})
    assert result == "Hello, {{unknown_var}}!"


def test_functions_registry():
    expected = {
        "random_int", "random_string", "timestamp", "uuid",
        "md5", "hmac_sha256", "base64_encode", "base64_decode",
        "date_format", "now_iso",
    }
    assert set(FUNCTIONS.keys()) == expected
