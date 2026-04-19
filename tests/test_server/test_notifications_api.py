from unittest.mock import patch, MagicMock

import pytest

from hermes_server.app import db
from hermes_server.models.project import Project
from hermes_server.models.user import User


@pytest.fixture()
def notification_project(auth_client, auth_headers):
    with auth_client.application.app_context():
        user = User.query.first()
        if not user:
            user = User(username="notifuser", email="notif@example.com", password_hash="hash")
            db.session.add(user)
            db.session.flush()

        project = Project(name="Notif Project", description="For notifications", owner_id=user.id)
        db.session.add(project)
        db.session.commit()

        return project.id


def test_create_notification(auth_client, auth_headers, notification_project):
    resp = auth_client.post(
        "/api/v1/notifications",
        json={
            "name": "Slack Webhook",
            "project_id": notification_project,
            "type": "webhook",
            "config": {"url": "http://localhost:9999/webhook"},
            "trigger_condition": {"on_fail": True},
            "is_enabled": True,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["name"] == "Slack Webhook"
    assert data["project_id"] == notification_project
    assert data["type"] == "webhook"
    assert data["config"]["url"] == "http://localhost:9999/webhook"
    assert data["is_enabled"] is True


def test_create_notification_missing_fields(auth_client, auth_headers, notification_project):
    resp = auth_client.post(
        "/api/v1/notifications",
        json={"name": "Incomplete"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_list_notifications(auth_client, auth_headers, notification_project):
    auth_client.post(
        "/api/v1/notifications",
        json={
            "name": "Notif A",
            "project_id": notification_project,
            "type": "webhook",
        },
        headers=auth_headers,
    )
    auth_client.post(
        "/api/v1/notifications",
        json={
            "name": "Notif B",
            "project_id": notification_project,
            "type": "email",
        },
        headers=auth_headers,
    )
    resp = auth_client.get(f"/api/v1/notifications?project_id={notification_project}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data["items"]) >= 2


def test_get_notification(auth_client, auth_headers, notification_project):
    create_resp = auth_client.post(
        "/api/v1/notifications",
        json={
            "name": "Get Notif",
            "project_id": notification_project,
            "type": "webhook",
        },
        headers=auth_headers,
    )
    notif_id = create_resp.get_json()["data"]["id"]
    resp = auth_client.get(f"/api/v1/notifications/{notif_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["id"] == notif_id
    assert data["name"] == "Get Notif"


def test_update_notification(auth_client, auth_headers, notification_project):
    create_resp = auth_client.post(
        "/api/v1/notifications",
        json={
            "name": "Original Notif",
            "project_id": notification_project,
            "type": "webhook",
        },
        headers=auth_headers,
    )
    notif_id = create_resp.get_json()["data"]["id"]
    resp = auth_client.put(
        f"/api/v1/notifications/{notif_id}",
        json={
            "name": "Updated Notif",
            "type": "email",
            "config": {"smtp_host": "smtp.example.com", "sender": "a@b.com", "receiver": "c@d.com"},
            "trigger_condition": {"on_error": True},
            "is_enabled": False,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["name"] == "Updated Notif"
    assert data["type"] == "email"
    assert data["is_enabled"] is False


def test_delete_notification(auth_client, auth_headers, notification_project):
    create_resp = auth_client.post(
        "/api/v1/notifications",
        json={
            "name": "Delete Notif",
            "project_id": notification_project,
            "type": "webhook",
        },
        headers=auth_headers,
    )
    notif_id = create_resp.get_json()["data"]["id"]
    resp = auth_client.delete(f"/api/v1/notifications/{notif_id}", headers=auth_headers)
    assert resp.status_code == 200
    get_resp = auth_client.get(f"/api/v1/notifications/{notif_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_test_notification_webhook(auth_client, auth_headers, notification_project):
    create_resp = auth_client.post(
        "/api/v1/notifications",
        json={
            "name": "Webhook Test",
            "project_id": notification_project,
            "type": "webhook",
            "config": {"url": "http://localhost:9999/webhook"},
        },
        headers=auth_headers,
    )
    notif_id = create_resp.get_json()["data"]["id"]
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "ok"
    with patch("hermes_server.api.v1.notifications.requests.post", return_value=mock_resp) as mock_post:
        resp = auth_client.post(f"/api/v1/notifications/{notif_id}/test", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["status_code"] == 200
        mock_post.assert_called_once()


def test_test_notification_email(auth_client, auth_headers, notification_project):
    create_resp = auth_client.post(
        "/api/v1/notifications",
        json={
            "name": "Email Test",
            "project_id": notification_project,
            "type": "email",
            "config": {
                "smtp_host": "smtp.example.com",
                "smtp_port": 587,
                "sender": "a@b.com",
                "receiver": "c@d.com",
                "smtp_user": "user",
                "smtp_password": "pass",
                "use_tls": True,
            },
        },
        headers=auth_headers,
    )
    notif_id = create_resp.get_json()["data"]["id"]
    mock_smtp_instance = MagicMock()
    with patch("hermes_server.api.v1.notifications.smtplib.SMTP", return_value=mock_smtp_instance):
        resp = auth_client.post(f"/api/v1/notifications/{notif_id}/test", headers=auth_headers)
        assert resp.status_code == 200
        mock_smtp_instance.__enter__.return_value.starttls.assert_called_once()
        mock_smtp_instance.__enter__.return_value.login.assert_called_once()
        mock_smtp_instance.__enter__.return_value.sendmail.assert_called_once()


def test_test_notification_webhook_missing_url(auth_client, auth_headers, notification_project):
    create_resp = auth_client.post(
        "/api/v1/notifications",
        json={
            "name": "No URL Webhook",
            "project_id": notification_project,
            "type": "webhook",
            "config": {},
        },
        headers=auth_headers,
    )
    notif_id = create_resp.get_json()["data"]["id"]
    resp = auth_client.post(f"/api/v1/notifications/{notif_id}/test", headers=auth_headers)
    assert resp.status_code == 400


def test_test_notification_email_missing_smtp_fields(auth_client, auth_headers, notification_project):
    create_resp = auth_client.post(
        "/api/v1/notifications",
        json={
            "name": "No SMTP Email",
            "project_id": notification_project,
            "type": "email",
            "config": {"smtp_host": "smtp.example.com"},
        },
        headers=auth_headers,
    )
    notif_id = create_resp.get_json()["data"]["id"]
    resp = auth_client.post(f"/api/v1/notifications/{notif_id}/test", headers=auth_headers)
    assert resp.status_code == 400


def test_test_notification_not_found(auth_client, auth_headers, notification_project):
    resp = auth_client.post("/api/v1/notifications/99999/test", headers=auth_headers)
    assert resp.status_code == 404
