import pytest


@pytest.fixture()
def project(auth_client, auth_headers):
    resp = auth_client.post(
        "/api/v1/projects",
        json={"name": "Env Test Project"},
        headers=auth_headers,
    )
    return resp.get_json()["data"]


class TestCreateEnvironment:
    def test_create_environment(self, auth_client, auth_headers, project):
        resp = auth_client.post(
            f"/api/v1/projects/{project['id']}/environments",
            json={"name": "Staging", "base_url": "http://staging.example.com", "variables": {"key": "val"}},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert data["name"] == "Staging"
        assert data["base_url"] == "http://staging.example.com"
        assert data["variables"] == {"key": "val"}

    def test_create_environment_missing_name(self, auth_client, auth_headers, project):
        resp = auth_client.post(
            f"/api/v1/projects/{project['id']}/environments",
            json={"base_url": "http://example.com"},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_create_environment_nonexistent_project(self, auth_client, auth_headers):
        resp = auth_client.post(
            "/api/v1/projects/99999/environments",
            json={"name": "Dev"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestListEnvironments:
    def test_list_environments(self, auth_client, auth_headers, project):
        auth_client.post(
            f"/api/v1/projects/{project['id']}/environments",
            json={"name": "Dev"},
            headers=auth_headers,
        )
        resp = auth_client.get(
            f"/api/v1/projects/{project['id']}/environments",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert len(data["items"]) >= 1


class TestGetEnvironment:
    def test_get_environment(self, auth_client, auth_headers, project):
        create_resp = auth_client.post(
            f"/api/v1/projects/{project['id']}/environments",
            json={"name": "Prod", "base_url": "http://prod.example.com"},
            headers=auth_headers,
        )
        env_id = create_resp.get_json()["data"]["id"]

        resp = auth_client.get(
            f"/api/v1/projects/{project['id']}/environments/{env_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["data"]["name"] == "Prod"

    def test_get_environment_not_found(self, auth_client, auth_headers, project):
        resp = auth_client.get(
            f"/api/v1/projects/{project['id']}/environments/99999",
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestUpdateEnvironment:
    def test_update_environment(self, auth_client, auth_headers, project):
        create_resp = auth_client.post(
            f"/api/v1/projects/{project['id']}/environments",
            json={"name": "Dev"},
            headers=auth_headers,
        )
        env_id = create_resp.get_json()["data"]["id"]

        resp = auth_client.put(
            f"/api/v1/projects/{project['id']}/environments/{env_id}",
            json={"name": "Dev Updated", "base_url": "http://dev2.example.com", "variables": {"k": "v"}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["name"] == "Dev Updated"
        assert data["base_url"] == "http://dev2.example.com"


class TestDeleteEnvironment:
    def test_delete_environment(self, auth_client, auth_headers, project):
        create_resp = auth_client.post(
            f"/api/v1/projects/{project['id']}/environments",
            json={"name": "ToDelete"},
            headers=auth_headers,
        )
        env_id = create_resp.get_json()["data"]["id"]

        resp = auth_client.delete(
            f"/api/v1/projects/{project['id']}/environments/{env_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200

        get_resp = auth_client.get(
            f"/api/v1/projects/{project['id']}/environments/{env_id}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 404
