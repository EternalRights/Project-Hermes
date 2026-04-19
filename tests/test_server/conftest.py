import sys
import os
import types
from unittest.mock import MagicMock

import pytest

HERMES_SERVER_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "hermes-server")
)
if HERMES_SERVER_DIR in sys.path:
    sys.path.remove(HERMES_SERVER_DIR)
sys.path.insert(0, HERMES_SERVER_DIR)

if "prometheus_flask_instrumentator" not in sys.modules:
    _mock_inst = MagicMock()
    sys.modules["prometheus_flask_instrumentator"] = _mock_inst

if "hermes_server" not in sys.modules:
    _hermes_server_ns = types.ModuleType("hermes_server")
    _hermes_server_ns.__path__ = [HERMES_SERVER_DIR]
    _hermes_server_ns.__package__ = "hermes_server"
    sys.modules["hermes_server"] = _hermes_server_ns

import app as _app_mod

sys.modules["hermes_server.app"] = _app_mod
sys.modules["hermes_server"].app = _app_mod

import app.response as _resp_mod

sys.modules["hermes_server.app.response"] = _resp_mod

import models as _real_models

sys.modules["hermes_server.models"] = _real_models
sys.modules["hermes_server"].models = _real_models

for _name, _mod in list(sys.modules.items()):
    if _name.startswith("models."):
        _alias = "hermes_server." + _name
        sys.modules[_alias] = _mod

for _name, _mod in list(sys.modules.items()):
    if _name.startswith("hermes_server.models."):
        _short = _name.replace("hermes_server.", "")
        sys.modules[_short] = _mod

import config as _cfg_mod

sys.modules["hermes_server.config"] = _cfg_mod
sys.modules["hermes_server"].config = _cfg_mod

import config.config as _cfg_cfg_mod

sys.modules["hermes_server.config.config"] = _cfg_cfg_mod

import middleware as _mw_mod

sys.modules["hermes_server.middleware"] = _mw_mod
sys.modules["hermes_server"].middleware = _mw_mod

from app import db as _db, jwt as _jwt, cors as _cors
from models.user import Role as _Role
from models.project import Project as _Project, Environment as _Environment, GlobalVariable as _GlobalVariable
from models.test_case import TestCase as _TestCase, TestSuite as _TestSuite
from models.execution import TestExecution as _TestExecution
from models.notification import NotificationConfig as _NotificationConfig
from models.scheduled_task import ScheduledTask as _ScheduledTask
from flask import Flask


def _create_test_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "test-secret-key-for-hermes-testing-2024"
    app.config["JWT_SECRET_KEY"] = "test-jwt-secret-key-for-hermes-testing-2024"

    _db.init_app(app)
    _jwt.init_app(app)
    _cors.init_app(app)

    @_jwt.user_identity_loader
    def _user_identity_loader(identity):
        return str(identity)

    from app.error_handlers import register_error_handlers

    register_error_handlers(app)

    from middleware.request_logger import register_request_logger

    register_request_logger(app)

    from api.v1.auth import bp as auth_bp
    from api.v1.projects import bp as projects_bp
    from api.v1.test_cases import bp as test_cases_bp
    from api.v1.test_suites import bp as test_suites_bp
    from api.v1.executions import bp as executions_bp
    from api.v1.environments import bp as environments_bp
    from api.v1.variables import bp as variables_bp
    from api.v1.reports import bp as reports_bp
    from api.v1.scheduled_tasks import bp as scheduled_tasks_bp
    from api.v1.notifications import bp as notifications_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(test_cases_bp)
    app.register_blueprint(test_suites_bp)
    app.register_blueprint(executions_bp)
    app.register_blueprint(environments_bp)
    app.register_blueprint(variables_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(scheduled_tasks_bp)
    app.register_blueprint(notifications_bp)

    return app


@pytest.fixture(scope="session")
def app():
    _app = _create_test_app()
    return _app


@pytest.fixture()
def client(app):
    with app.app_context():
        _db.create_all()
        yield app.test_client()
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def auth_client(client):
    with client.application.app_context():
        role = _Role(name="test_engineer", description="Test Engineer")
        _db.session.add(role)
        _db.session.commit()
    return client


@pytest.fixture()
def registered_user(auth_client):
    resp = auth_client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "Test1234"},
    )
    data = resp.get_json()
    return data["data"]


@pytest.fixture()
def auth_token(auth_client, registered_user):
    resp = auth_client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "Test1234"},
    )
    data = resp.get_json()
    return data["data"]["access_token"]


@pytest.fixture()
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture()
def test_project(auth_client, auth_headers):
    resp = auth_client.post(
        "/api/v1/projects",
        json={"name": "Test Project", "description": "A project for testing"},
        headers=auth_headers,
    )
    data = resp.get_json()
    return data["data"]


@pytest.fixture()
def test_environment(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    resp = auth_client.post(
        f"/api/v1/projects/{project_id}/environments",
        json={"name": "Testing", "base_url": "http://localhost:5000", "variables": {"key": "value"}},
        headers=auth_headers,
    )
    data = resp.get_json()
    return data["data"]


@pytest.fixture()
def test_global_variable(auth_client, auth_headers, test_project, test_environment):
    project_id = test_project["id"]
    environment_id = test_environment["id"]
    resp = auth_client.post(
        f"/api/v1/projects/{project_id}/variables",
        json={"key": "BASE_URL", "value": "http://localhost:5000", "environment_id": environment_id, "description": "Base URL variable"},
        headers=auth_headers,
    )
    data = resp.get_json()
    return data["data"]


@pytest.fixture()
def test_case_data(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    resp = auth_client.post(
        "/api/v1/test-cases",
        json={
            "name": "Sample Test Case",
            "project_id": project_id,
            "module": "auth",
            "tags": ["smoke", "api"],
            "priority": "P1",
            "request_config": {
                "method": "GET",
                "url": "http://localhost:5000/api/v1/projects",
                "headers": {"Content-Type": "application/json"},
            },
            "assertions": [
                {"type": "status_code", "expected": 200},
            ],
            "variables": {},
        },
        headers=auth_headers,
    )
    data = resp.get_json()
    return data["data"]


@pytest.fixture()
def test_suite_data(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    resp = auth_client.post(
        "/api/v1/test-suites",
        json={
            "name": "Sample Test Suite",
            "project_id": project_id,
            "description": "A suite for testing",
            "execution_mode": "serial",
        },
        headers=auth_headers,
    )
    data = resp.get_json()
    return data["data"]


@pytest.fixture()
def test_execution_data(auth_client, auth_headers, test_project, test_suite_data, test_environment):
    resp = auth_client.post(
        "/api/v1/executions",
        json={
            "suite_id": test_suite_data["id"],
            "environment_id": test_environment["id"],
        },
        headers=auth_headers,
    )
    data = resp.get_json()
    return data["data"]


@pytest.fixture()
def test_notification_config(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    resp = auth_client.post(
        "/api/v1/notifications",
        json={
            "name": "Test Notification",
            "project_id": project_id,
            "type": "webhook",
            "config": {"url": "http://localhost:9999/webhook"},
            "trigger_condition": {"on_fail": True, "on_error": True},
            "is_enabled": True,
        },
        headers=auth_headers,
    )
    data = resp.get_json()
    return data["data"]


@pytest.fixture()
def test_scheduled_task_data(auth_client, auth_headers, test_project, test_suite_data, test_environment):
    project_id = test_project["id"]
    resp = auth_client.post(
        "/api/v1/scheduled-tasks",
        json={
            "name": "Test Scheduled Task",
            "project_id": project_id,
            "suite_id": test_suite_data["id"],
            "environment_id": test_environment["id"],
            "cron_expression": "0 */6 * * *",
            "is_enabled": True,
        },
        headers=auth_headers,
    )
    data = resp.get_json()
    return data["data"]
