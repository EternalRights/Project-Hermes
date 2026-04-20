import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture()
def project(auth_client, auth_headers):
    resp = auth_client.post(
        "/api/v1/projects",
        json={"name": "Exec Test Project"},
        headers=auth_headers,
    )
    return resp.get_json()["data"]


@pytest.fixture()
def environment(auth_client, auth_headers, project):
    resp = auth_client.post(
        f"/api/v1/projects/{project['id']}/environments",
        json={"name": "Dev", "base_url": "http://localhost:5000"},
        headers=auth_headers,
    )
    return resp.get_json()["data"]


@pytest.fixture()
def test_case(auth_client, auth_headers, project):
    resp = auth_client.post(
        "/api/v1/test-cases",
        json={
            "name": "Exec Test Case",
            "project_id": project["id"],
            "priority": "P1",
            "request_config": {"method": "GET", "url": "/api/v1/projects"},
            "assertions": [{"type": "status_code", "expected": 200}],
        },
        headers=auth_headers,
    )
    return resp.get_json()["data"]


@pytest.fixture()
def suite(auth_client, auth_headers, project, test_case):
    resp = auth_client.post(
        "/api/v1/test-suites",
        json={"name": "Exec Test Suite", "project_id": project["id"]},
        headers=auth_headers,
    )
    suite_data = resp.get_json()["data"]
    auth_client.post(
        f"/api/v1/test-suites/{suite_data['id']}/cases",
        json={"case_id": test_case["id"], "sort_order": 1},
        headers=auth_headers,
    )
    return suite_data


class TestCreateExecution:
    @patch("api.v1.executions.Celery")
    def test_create_execution(self, mock_celery_cls, auth_client, auth_headers, suite, environment):
        mock_celery_inst = MagicMock()
        mock_celery_cls.return_value = mock_celery_inst

        resp = auth_client.post(
            "/api/v1/executions",
            json={"suite_id": suite["id"], "environment_id": environment["id"]},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert data["suite_id"] == suite["id"]
        assert data["environment_id"] == environment["id"]
        assert data["status"] == "pending"
        mock_celery_inst.send_task.assert_called_once()

    def test_create_execution_missing_suite_id(self, auth_client, auth_headers, environment):
        resp = auth_client.post(
            "/api/v1/executions",
            json={"environment_id": environment["id"]},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_create_execution_missing_environment_id(self, auth_client, auth_headers, suite):
        resp = auth_client.post(
            "/api/v1/executions",
            json={"suite_id": suite["id"]},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    @patch("api.v1.executions.Celery")
    def test_create_execution_nonexistent_suite(self, mock_celery_cls, auth_client, auth_headers, environment):
        resp = auth_client.post(
            "/api/v1/executions",
            json={"suite_id": 99999, "environment_id": environment["id"]},
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestGetExecution:
    @patch("api.v1.executions.Celery")
    def test_get_execution(self, mock_celery_cls, auth_client, auth_headers, suite, environment):
        mock_celery_cls.return_value = MagicMock()
        create_resp = auth_client.post(
            "/api/v1/executions",
            json={"suite_id": suite["id"], "environment_id": environment["id"]},
            headers=auth_headers,
        )
        execution_id = create_resp.get_json()["data"]["id"]

        resp = auth_client.get(f"/api/v1/executions/{execution_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["id"] == execution_id
        assert "step_results" in data

    def test_get_execution_not_found(self, auth_client, auth_headers):
        resp = auth_client.get("/api/v1/executions/99999", headers=auth_headers)
        assert resp.status_code == 404


class TestListExecutions:
    @patch("api.v1.executions.Celery")
    def test_list_executions(self, mock_celery_cls, auth_client, auth_headers, suite, environment):
        mock_celery_cls.return_value = MagicMock()
        auth_client.post(
            "/api/v1/executions",
            json={"suite_id": suite["id"], "environment_id": environment["id"]},
            headers=auth_headers,
        )

        resp = auth_client.get("/api/v1/executions", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert "items" in data
        assert len(data["items"]) >= 1

    @patch("api.v1.executions.Celery")
    def test_list_executions_filter_by_suite(self, mock_celery_cls, auth_client, auth_headers, suite, environment):
        mock_celery_cls.return_value = MagicMock()
        resp = auth_client.get(
            f"/api/v1/executions?suite_id={suite['id']}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
