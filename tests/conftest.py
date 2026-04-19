import sys
import os
import types

import pytest


HERMES_CORE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "hermes-core")
)
if HERMES_CORE_DIR not in sys.path:
    sys.path.insert(0, HERMES_CORE_DIR)

if "hermes_core" not in sys.modules:
    _hermes_core_ns = types.ModuleType("hermes_core")
    _hermes_core_ns.__path__ = [HERMES_CORE_DIR]
    _hermes_core_ns.__package__ = "hermes_core"
    _hermes_core_ns.__version__ = "0.1.0"
    sys.modules["hermes_core"] = _hermes_core_ns

    _sub_packages = [
        "assertions", "executor", "parametrize", "scheduler", "tracing", "utils"
    ]
    for _pkg in _sub_packages:
        _full = f"hermes_core.{_pkg}"
        if _full not in sys.modules:
            _pkg_dir = os.path.join(HERMES_CORE_DIR, _pkg)
            if os.path.isdir(_pkg_dir):
                _mod = types.ModuleType(_full)
                _mod.__path__ = [_pkg_dir]
                _mod.__package__ = _full
                sys.modules[_full] = _mod
                setattr(_hermes_core_ns, _pkg, _mod)


@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:5000"


@pytest.fixture(scope="session")
def api_prefix():
    return "/api/v1"


@pytest.fixture(scope="session")
def test_headers():
    return {"Content-Type": "application/json"}
