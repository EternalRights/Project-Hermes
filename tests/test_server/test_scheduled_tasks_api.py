import pytest

from hermes_server.app import db
from hermes_server.models.project import Project, Environment
from hermes_server.models.test_case import TestCase, TestSuite
from hermes_server.models.user import User


@pytest.fixture()
def scheduled_task_prereqs(auth_client, auth_headers):
    with auth_client.application.app_context():
        user = User.query.first()
        if not user:
            user = User(username="taskuser", email="task@example.com", password_hash="hash")
            db.session.add(user)
            db.session.flush()

        project = Project(name="Task Project", description="For scheduled tasks", owner_id=user.id)
        db.session.add(project)
        db.session.flush()

        env = Environment(name="Task Env", project_id=project.id, base_url="http://localhost:5000")
        db.session.add(env)
        db.session.flush()

        suite = TestSuite(name="Task Suite", project_id=project.id, created_by=user.id)
        db.session.add(suite)
        db.session.commit()

        return {
            "project_id": project.id,
            "environment_id": env.id,
            "suite_id": suite.id,
        }


def test_create_scheduled_task(auth_client, auth_headers, scheduled_task_prereqs):
    resp = auth_client.post(
        "/api/v1/scheduled-tasks",
        json={
            "name": "Nightly Run",
            "project_id": scheduled_task_prereqs["project_id"],
            "suite_id": scheduled_task_prereqs["suite_id"],
            "environment_id": scheduled_task_prereqs["environment_id"],
            "cron_expression": "0 0 * * *",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["name"] == "Nightly Run"
    assert data["project_id"] == scheduled_task_prereqs["project_id"]
    assert data["suite_id"] == scheduled_task_prereqs["suite_id"]
    assert data["environment_id"] == scheduled_task_prereqs["environment_id"]
    assert data["cron_expression"] == "0 0 * * *"
    assert data["is_enabled"] is True


def test_create_scheduled_task_missing_fields(auth_client, auth_headers, scheduled_task_prereqs):
    resp = auth_client.post(
        "/api/v1/scheduled-tasks",
        json={"name": "Incomplete Task"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_list_scheduled_tasks(auth_client, auth_headers, scheduled_task_prereqs):
    project_id = scheduled_task_prereqs["project_id"]
    auth_client.post(
        "/api/v1/scheduled-tasks",
        json={
            "name": "Task A",
            "project_id": project_id,
            "suite_id": scheduled_task_prereqs["suite_id"],
            "environment_id": scheduled_task_prereqs["environment_id"],
            "cron_expression": "0 */6 * * *",
        },
        headers=auth_headers,
    )
    auth_client.post(
        "/api/v1/scheduled-tasks",
        json={
            "name": "Task B",
            "project_id": project_id,
            "suite_id": scheduled_task_prereqs["suite_id"],
            "environment_id": scheduled_task_prereqs["environment_id"],
            "cron_expression": "0 0 * * *",
        },
        headers=auth_headers,
    )
    resp = auth_client.get(f"/api/v1/scheduled-tasks?project_id={project_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert len(data["items"]) >= 2


def test_get_scheduled_task(auth_client, auth_headers, scheduled_task_prereqs):
    create_resp = auth_client.post(
        "/api/v1/scheduled-tasks",
        json={
            "name": "Get Task",
            "project_id": scheduled_task_prereqs["project_id"],
            "suite_id": scheduled_task_prereqs["suite_id"],
            "environment_id": scheduled_task_prereqs["environment_id"],
            "cron_expression": "0 0 * * *",
        },
        headers=auth_headers,
    )
    task_id = create_resp.get_json()["data"]["id"]
    resp = auth_client.get(f"/api/v1/scheduled-tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["id"] == task_id
    assert data["name"] == "Get Task"


def test_update_scheduled_task(auth_client, auth_headers, scheduled_task_prereqs):
    create_resp = auth_client.post(
        "/api/v1/scheduled-tasks",
        json={
            "name": "Original Task",
            "project_id": scheduled_task_prereqs["project_id"],
            "suite_id": scheduled_task_prereqs["suite_id"],
            "environment_id": scheduled_task_prereqs["environment_id"],
            "cron_expression": "0 0 * * *",
        },
        headers=auth_headers,
    )
    task_id = create_resp.get_json()["data"]["id"]
    resp = auth_client.put(
        f"/api/v1/scheduled-tasks/{task_id}",
        json={"name": "Updated Task", "cron_expression": "0 */2 * * *"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["name"] == "Updated Task"
    assert data["cron_expression"] == "0 */2 * * *"


def test_delete_scheduled_task(auth_client, auth_headers, scheduled_task_prereqs):
    create_resp = auth_client.post(
        "/api/v1/scheduled-tasks",
        json={
            "name": "Delete Task",
            "project_id": scheduled_task_prereqs["project_id"],
            "suite_id": scheduled_task_prereqs["suite_id"],
            "environment_id": scheduled_task_prereqs["environment_id"],
            "cron_expression": "0 0 * * *",
        },
        headers=auth_headers,
    )
    task_id = create_resp.get_json()["data"]["id"]
    resp = auth_client.delete(f"/api/v1/scheduled-tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 200
    get_resp = auth_client.get(f"/api/v1/scheduled-tasks/{task_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_toggle_scheduled_task(auth_client, auth_headers, scheduled_task_prereqs):
    create_resp = auth_client.post(
        "/api/v1/scheduled-tasks",
        json={
            "name": "Toggle Task",
            "project_id": scheduled_task_prereqs["project_id"],
            "suite_id": scheduled_task_prereqs["suite_id"],
            "environment_id": scheduled_task_prereqs["environment_id"],
            "cron_expression": "0 0 * * *",
        },
        headers=auth_headers,
    )
    task_id = create_resp.get_json()["data"]["id"]
    resp = auth_client.put(
        f"/api/v1/scheduled-tasks/{task_id}/toggle",
        json={"is_enabled": False},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["is_enabled"] is False


def test_toggle_scheduled_task_missing_is_enabled(auth_client, auth_headers, scheduled_task_prereqs):
    create_resp = auth_client.post(
        "/api/v1/scheduled-tasks",
        json={
            "name": "Toggle Missing Task",
            "project_id": scheduled_task_prereqs["project_id"],
            "suite_id": scheduled_task_prereqs["suite_id"],
            "environment_id": scheduled_task_prereqs["environment_id"],
            "cron_expression": "0 0 * * *",
        },
        headers=auth_headers,
    )
    task_id = create_resp.get_json()["data"]["id"]
    resp = auth_client.put(
        f"/api/v1/scheduled-tasks/{task_id}/toggle",
        json={},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_get_scheduled_task_history(auth_client, auth_headers, scheduled_task_prereqs):
    create_resp = auth_client.post(
        "/api/v1/scheduled-tasks",
        json={
            "name": "History Task",
            "project_id": scheduled_task_prereqs["project_id"],
            "suite_id": scheduled_task_prereqs["suite_id"],
            "environment_id": scheduled_task_prereqs["environment_id"],
            "cron_expression": "0 0 * * *",
        },
        headers=auth_headers,
    )
    task_id = create_resp.get_json()["data"]["id"]
    resp = auth_client.get(f"/api/v1/scheduled-tasks/{task_id}/history", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "items" in data
    assert "total" in data
    assert "page" in data
