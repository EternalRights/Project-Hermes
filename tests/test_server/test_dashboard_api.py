import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture()
def project(auth_client, auth_headers):
    resp = auth_client.post(
        "/api/v1/projects",
        json={"name": "Dashboard Test Project"},
        headers=auth_headers,
    )
    return resp.get_json()["data"]


class TestDashboardStats:
    def test_get_dashboard_stats(self, auth_client, auth_headers, project):
        resp = auth_client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert "todayExecutions" in data
        assert "passRate" in data
        assert "activeCases" in data
        assert "activeSuites" in data
        assert "recentExecutions" in data

    def test_dashboard_stats_requires_auth(self, auth_client):
        resp = auth_client.get("/api/v1/dashboard/stats")
        assert resp.status_code in (401, 422)
