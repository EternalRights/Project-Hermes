import pytest


class TestAuthMeEndpoint:
    def test_get_current_user_info(self, auth_client, auth_headers, registered_user):
        resp = auth_client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert "id" in data
        assert data["username"] == "testuser"
        assert "email" in data
        assert "roles" in data

    def test_auth_me_requires_token(self, auth_client):
        resp = auth_client.get("/api/v1/auth/me")
        assert resp.status_code in (401, 422)

    def test_auth_me_with_invalid_token(self, auth_client):
        resp = auth_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert resp.status_code in (401, 422)
