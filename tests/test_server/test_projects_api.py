import pytest


def test_create_project(auth_client, auth_headers):
    resp = auth_client.post(
        "/api/v1/projects",
        json={"name": "Test Project", "description": "A test project"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["data"]["name"] == "Test Project"
    assert data["data"]["description"] == "A test project"
    assert data["data"]["is_active"] is True


def test_get_projects(auth_client, auth_headers):
    auth_client.post(
        "/api/v1/projects",
        json={"name": "Project A"},
        headers=auth_headers,
    )
    auth_client.post(
        "/api/v1/projects",
        json={"name": "Project B"},
        headers=auth_headers,
    )
    resp = auth_client.get("/api/v1/projects", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["data"]["items"]) >= 2


def test_update_project(auth_client, auth_headers):
    create_resp = auth_client.post(
        "/api/v1/projects",
        json={"name": "Original Name"},
        headers=auth_headers,
    )
    project_id = create_resp.get_json()["data"]["id"]
    resp = auth_client.put(
        f"/api/v1/projects/{project_id}",
        json={"name": "Updated Name", "description": "Updated desc"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["data"]["name"] == "Updated Name"
    assert data["data"]["description"] == "Updated desc"


def test_delete_project(auth_client, auth_headers):
    create_resp = auth_client.post(
        "/api/v1/projects",
        json={"name": "To Delete"},
        headers=auth_headers,
    )
    project_id = create_resp.get_json()["data"]["id"]
    resp = auth_client.delete(
        f"/api/v1/projects/{project_id}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    get_resp = auth_client.get(
        f"/api/v1/projects/{project_id}",
        headers=auth_headers,
    )
    assert get_resp.status_code == 404
