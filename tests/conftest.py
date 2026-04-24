import sys
import os
import types

import pytest


collect_ignore_glob = ["**/hermes_server/models/*", "**/hermes_core/executor/*"]


def pytest_collection_modifyitems(session, config, items):
    skip_names = {
        "TestCase", "TestCaseResult", "TestCaseRunner",
        "TestSuite", "TestExecution", "TestStepResult",
    }
    items[:] = [item for item in items if item.cls is None or item.cls.__name__ not in skip_names]


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

HERMES_CORE_DIR = os.path.join(PROJECT_ROOT, "hermes-core")
HERMES_SERVER_DIR = os.path.join(PROJECT_ROOT, "hermes-server")
HERMES_WORKER_DIR = os.path.join(PROJECT_ROOT, "hermes-worker")


def _ensure_path(directory):
    if directory not in sys.path:
        sys.path.insert(0, directory)


def _register_namespace(name, directory, sub_packages=None):
    if name not in sys.modules:
        ns = types.ModuleType(name)
        ns.__path__ = [directory]
        ns.__package__ = name
        ns.__version__ = "0.1.0"
        sys.modules[name] = ns
    else:
        ns = sys.modules[name]

    if sub_packages:
        for pkg in sub_packages:
            full = f"{name}.{pkg}"
            if full not in sys.modules:
                pkg_dir = os.path.join(directory, pkg)
                if os.path.isdir(pkg_dir):
                    mod = types.ModuleType(full)
                    mod.__path__ = [pkg_dir]
                    mod.__package__ = full
                    sys.modules[full] = mod
                    setattr(ns, pkg, mod)

    return ns


_ensure_path(HERMES_CORE_DIR)
_register_namespace("hermes_core", HERMES_CORE_DIR, [
    "assertions", "executor", "parametrize", "scheduler", "tracing", "utils",
])

_ensure_path(HERMES_SERVER_DIR)
_register_namespace("hermes_server", HERMES_SERVER_DIR, [
    "api", "app", "config", "middleware", "models", "services",
])

_ensure_path(HERMES_WORKER_DIR)
_register_namespace("hermes_worker", HERMES_WORKER_DIR, [
    "tasks",
])


@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:5000"


@pytest.fixture(scope="session")
def api_prefix():
    return "/api/v1"


@pytest.fixture(scope="session")
def test_headers():
    return {"Content-Type": "application/json"}
