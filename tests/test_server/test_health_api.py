import pytest


class TestHealthEndpoint:
    def test_health_check_healthy(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert data["database"] == "connected"

    def test_health_check_no_auth_required(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
