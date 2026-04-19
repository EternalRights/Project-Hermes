import pytest


def test_register_success(auth_client):
    resp = auth_client.post(
        "/api/v1/auth/register",
        json={"username": "newuser", "email": "new@example.com", "password": "Password1"},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["code"] == 201
    assert data["data"]["username"] == "newuser"
    assert data["data"]["email"] == "new@example.com"


def test_register_duplicate_username(auth_client):
    auth_client.post(
        "/api/v1/auth/register",
        json={"username": "dupuser", "email": "dup1@example.com", "password": "Password1"},
    )
    resp = auth_client.post(
        "/api/v1/auth/register",
        json={"username": "dupuser", "email": "dup2@example.com", "password": "Password1"},
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert "already exists" in data["message"]


def test_login_success(auth_client, registered_user):
    resp = auth_client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "Test1234"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["user"]["username"] == "testuser"


def test_login_wrong_password(auth_client, registered_user):
    resp = auth_client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "WrongPassword"},
    )
    assert resp.status_code == 401
    data = resp.get_json()
    assert "invalid" in data["message"]


def test_refresh_token(auth_client, registered_user):
    login_resp = auth_client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "Test1234"},
    )
    refresh_token = login_resp.get_json()["data"]["refresh_token"]
    resp = auth_client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "access_token" in data["data"]


def test_protected_endpoint_without_token(client):
    resp = client.get("/api/v1/projects")
    assert resp.status_code == 401


def test_protected_endpoint_with_token(auth_client, auth_headers):
    resp = auth_client.get("/api/v1/projects", headers=auth_headers)
    assert resp.status_code == 200
