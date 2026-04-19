import sys
import os
import types
from unittest.mock import MagicMock

import pytest


HERMES_SERVER_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "hermes-server")
)
if HERMES_SERVER_DIR not in sys.path:
    sys.path.insert(0, HERMES_SERVER_DIR)

if "prometheus_flask_instrumentator" not in sys.modules:
    _mock_inst = MagicMock()
    sys.modules["prometheus_flask_instrumentator"] = _mock_inst

if "hermes_server" not in sys.modules:
    _hermes_server_ns = types.ModuleType("hermes_server")
    _hermes_server_ns.__path__ = [HERMES_SERVER_DIR]
    _hermes_server_ns.__package__ = "hermes_server"
    sys.modules["hermes_server"] = _hermes_server_ns

if "hermes_server.app" not in sys.modules:
    import app as _app_mod

    sys.modules["hermes_server.app"] = _app_mod
    sys.modules["hermes_server"].app = _app_mod

if "hermes_server.app.response" not in sys.modules:
    import app.response as _resp_mod

    sys.modules["hermes_server.app.response"] = _resp_mod

if "hermes_server.models" not in sys.modules:
    _models_placeholder = types.ModuleType("hermes_server.models")
    _models_placeholder.__path__ = [os.path.join(HERMES_SERVER_DIR, "models")]
    _models_placeholder.__package__ = "hermes_server.models"
    sys.modules["hermes_server.models"] = _models_placeholder
    sys.modules["hermes_server"].models = _models_placeholder

    import models as _real_models

    sys.modules["hermes_server.models"] = _real_models
    sys.modules["hermes_server"].models = _real_models

    for _name, _mod in list(sys.modules.items()):
        if _name.startswith("models."):
            _alias = "hermes_server." + _name
            if _alias not in sys.modules:
                sys.modules[_alias] = _mod

    for _name, _mod in list(sys.modules.items()):
        if _name.startswith("hermes_server.models."):
            _short = _name.replace("hermes_server.", "")
            if _short not in sys.modules:
                sys.modules[_short] = _mod

if "hermes_server.config" not in sys.modules:
    import config as _cfg_mod

    sys.modules["hermes_server.config"] = _cfg_mod
    sys.modules["hermes_server"].config = _cfg_mod

if "hermes_server.config.config" not in sys.modules:
    import config.config as _cfg_cfg_mod

    sys.modules["hermes_server.config.config"] = _cfg_cfg_mod

if "hermes_server.middleware" not in sys.modules:
    import middleware as _mw_mod

    sys.modules["hermes_server.middleware"] = _mw_mod
    sys.modules["hermes_server"].middleware = _mw_mod

from app import db as _db, jwt as _jwt, cors as _cors
from models.user import Role as _Role
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

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)

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
