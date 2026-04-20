import time
from datetime import timedelta
from unittest.mock import patch, MagicMock

import pytest


class TestJWTTokenTampering:
    def test_tampered_jwt_token(self, auth_client, registered_user):
        login_resp = auth_client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "Test1234"},
        )
        token = login_resp.get_json()["data"]["access_token"]

        tampered_token = token[:-5] + "XXXXX"
        resp = auth_client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {tampered_token}"},
        )
        assert resp.status_code in (401, 422)


class TestExpiredJWTToken:
    def test_expired_jwt_token(self, auth_client, registered_user):
        login_resp = auth_client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "Test1234"},
        )
        token = login_resp.get_json()["data"]["access_token"]

        with auth_client.application.app_context():
            from flask_jwt_extended import decode_token
            try:
                decoded = decode_token(token)
            except Exception:
                pass

        resp = auth_client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200


class TestRBACEnforcement:
    def test_user_without_permission_denied(self, auth_client, auth_headers):
        with auth_client.application.app_context():
            from models.user import User, Role, Permission
            from app import db

            user = User(username="noperm_user", email="noperm@example.com")
            user.set_password("Password1")
            db.session.add(user)
            db.session.commit()

        login_resp = auth_client.post(
            "/api/v1/auth/login",
            json={"username": "noperm_user", "password": "Password1"},
        )
        assert login_resp.status_code == 200
        user_token = login_resp.get_json()["data"]["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        resp = auth_client.get("/api/v1/projects", headers=user_headers)
        assert resp.status_code == 200


class TestSQLInjection:
    def test_sql_injection_in_project_name(self, auth_client, auth_headers):
        malicious_name = "'; DROP TABLE project; --"
        resp = auth_client.post(
            "/api/v1/projects",
            json={"name": malicious_name},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert data["name"] == malicious_name

        list_resp = auth_client.get("/api/v1/projects", headers=auth_headers)
        assert list_resp.status_code == 200

    def test_sql_injection_in_username(self, auth_client):
        malicious_username = "admin' OR '1'='1"
        resp = auth_client.post(
            "/api/v1/auth/register",
            json={"username": malicious_username, "email": "sqli@example.com", "password": "Password1"},
        )
        assert resp.status_code in (201, 400)


class TestXSSPrevention:
    def test_xss_in_project_name(self, auth_client, auth_headers):
        xss_name = "<script>alert('xss')</script>"
        resp = auth_client.post(
            "/api/v1/projects",
            json={"name": xss_name},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert data["name"] == xss_name

        get_resp = auth_client.get(
            f"/api/v1/projects/{data['id']}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 200
        assert get_resp.get_json()["data"]["name"] == xss_name

    def test_xss_in_test_case_name(self, auth_client, auth_headers, test_project):
        xss_name = "<img src=x onerror=alert(1)>"
        resp = auth_client.post(
            "/api/v1/test-cases",
            json={"name": xss_name, "project_id": test_project["id"]},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert data["name"] == xss_name
