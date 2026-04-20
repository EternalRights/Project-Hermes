import pytest


@pytest.fixture()
def project(auth_client, auth_headers):
    resp = auth_client.post(
        "/api/v1/projects",
        json={"name": "Var Test Project"},
        headers=auth_headers,
    )
    return resp.get_json()["data"]


@pytest.fixture()
def environment(auth_client, auth_headers, project):
    resp = auth_client.post(
        f"/api/v1/projects/{project['id']}/environments",
        json={"name": "Dev"},
        headers=auth_headers,
    )
    return resp.get_json()["data"]


class TestCreateVariable:
    def test_create_variable(self, auth_client, auth_headers, project):
        resp = auth_client.post(
            f"/api/v1/projects/{project['id']}/variables",
            json={"key": "API_KEY", "value": "secret123", "description": "API key"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert data["key"] == "API_KEY"
        assert data["value"] == "secret123"
        assert data["description"] == "API key"

    def test_create_variable_with_environment(self, auth_client, auth_headers, project, environment):
        resp = auth_client.post(
            f"/api/v1/projects/{project['id']}/variables",
            json={"key": "BASE_URL", "value": "http://dev.example.com", "environment_id": environment["id"]},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert data["environment_id"] == environment["id"]

    def test_create_variable_missing_key(self, auth_client, auth_headers, project):
        resp = auth_client.post(
            f"/api/v1/projects/{project['id']}/variables",
            json={"value": "some_value"},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_create_variable_nonexistent_project(self, auth_client, auth_headers):
        resp = auth_client.post(
            "/api/v1/projects/99999/variables",
            json={"key": "KEY", "value": "val"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestListVariables:
    def test_list_variables(self, auth_client, auth_headers, project):
        auth_client.post(
            f"/api/v1/projects/{project['id']}/variables",
            json={"key": "KEY1", "value": "val1"},
            headers=auth_headers,
        )
        resp = auth_client.get(
            f"/api/v1/projects/{project['id']}/variables",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert len(data["items"]) >= 1

    def test_list_variables_filter_by_environment(self, auth_client, auth_headers, project, environment):
        auth_client.post(
            f"/api/v1/projects/{project['id']}/variables",
            json={"key": "ENV_VAR", "value": "env_val", "environment_id": environment["id"]},
            headers=auth_headers,
        )
        auth_client.post(
            f"/api/v1/projects/{project['id']}/variables",
            json={"key": "GLOBAL_VAR", "value": "global_val"},
            headers=auth_headers,
        )
        resp = auth_client.get(
            f"/api/v1/projects/{project['id']}/variables?environment_id={environment['id']}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        items = resp.get_json()["data"]["items"]
        for item in items:
            assert item["environment_id"] == environment["id"]


class TestUpdateVariable:
    def test_update_variable(self, auth_client, auth_headers, project):
        create_resp = auth_client.post(
            f"/api/v1/projects/{project['id']}/variables",
            json={"key": "KEY1", "value": "old_val"},
            headers=auth_headers,
        )
        var_id = create_resp.get_json()["data"]["id"]

        resp = auth_client.put(
            f"/api/v1/projects/{project['id']}/variables/{var_id}",
            json={"value": "new_val", "description": "updated"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["value"] == "new_val"
        assert data["description"] == "updated"

    def test_update_variable_not_found(self, auth_client, auth_headers, project):
        resp = auth_client.put(
            f"/api/v1/projects/{project['id']}/variables/99999",
            json={"value": "new_val"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestDeleteVariable:
    def test_delete_variable(self, auth_client, auth_headers, project):
        create_resp = auth_client.post(
            f"/api/v1/projects/{project['id']}/variables",
            json={"key": "TO_DELETE", "value": "val"},
            headers=auth_headers,
        )
        var_id = create_resp.get_json()["data"]["id"]

        resp = auth_client.delete(
            f"/api/v1/projects/{project['id']}/variables/{var_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200

        get_resp = auth_client.get(
            f"/api/v1/projects/{project['id']}/variables",
            headers=auth_headers,
        )
        items = get_resp.get_json()["data"]["items"]
        assert all(v["id"] != var_id for v in items)
