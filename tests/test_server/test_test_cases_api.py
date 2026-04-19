import pytest


@pytest.fixture()
def created_case(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    resp = auth_client.post(
        "/api/v1/test-cases",
        json={
            "name": "Fixture Case",
            "project_id": project_id,
            "module": "auth",
            "tags": ["smoke", "api"],
            "priority": "P1",
        },
        headers=auth_headers,
    )
    return resp.get_json()["data"]


def test_create_test_case(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    resp = auth_client.post(
        "/api/v1/test-cases",
        json={"name": "My Test Case", "project_id": project_id},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["data"]["name"] == "My Test Case"
    assert data["data"]["project_id"] == project_id
    assert data["data"]["status"] == "draft"
    assert data["data"]["priority"] == "P2"
    assert data["data"]["timeout"] == 30000


def test_create_test_case_missing_name(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    resp = auth_client.post(
        "/api/v1/test-cases",
        json={"project_id": project_id},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_create_test_case_missing_project_id(auth_client, auth_headers):
    resp = auth_client.post(
        "/api/v1/test-cases",
        json={"name": "No Project"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_create_test_case_with_all_optional_fields(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    payload = {
        "name": "Full Case",
        "project_id": project_id,
        "module": "users",
        "tags": ["regression", "critical"],
        "priority": "P0",
        "request_config": {
            "method": "POST",
            "url": "http://localhost:5000/api/v1/users",
            "headers": {"Content-Type": "application/json"},
        },
        "assertions": [
            {"type": "status_code", "expected": 201},
            {"type": "json_path", "path": "$.id", "expected": "not_null"},
        ],
        "pre_hooks": [{"type": "setup_db", "config": {"table": "users"}}],
        "post_hooks": [{"type": "cleanup_db", "config": {"table": "users"}}],
        "variables": {"user_id": "123"},
        "retry_config": {"max_retries": 3, "interval": 1000},
        "timeout": 60000,
    }
    resp = auth_client.post(
        "/api/v1/test-cases",
        json=payload,
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["name"] == "Full Case"
    assert data["module"] == "users"
    assert data["tags"] == ["regression", "critical"]
    assert data["priority"] == "P0"
    assert data["request_config"]["method"] == "POST"
    assert len(data["assertions"]) == 2
    assert data["pre_hooks"][0]["type"] == "setup_db"
    assert data["post_hooks"][0]["type"] == "cleanup_db"
    assert data["variables"] == {"user_id": "123"}
    assert data["retry_config"]["max_retries"] == 3
    assert data["timeout"] == 60000


def test_list_test_cases(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    auth_client.post(
        "/api/v1/test-cases",
        json={"name": "Case A", "project_id": project_id},
        headers=auth_headers,
    )
    auth_client.post(
        "/api/v1/test-cases",
        json={"name": "Case B", "project_id": project_id},
        headers=auth_headers,
    )
    resp = auth_client.get("/api/v1/test-cases", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "items" in data["data"]
    assert data["data"]["total"] >= 2


def test_list_test_cases_filter_by_project_id(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    auth_client.post(
        "/api/v1/test-cases",
        json={"name": "Filtered Case", "project_id": project_id},
        headers=auth_headers,
    )
    resp = auth_client.get(
        f"/api/v1/test-cases?project_id={project_id}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    for item in data["data"]["items"]:
        assert item["project_id"] == project_id


def test_list_test_cases_filter_by_module(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    auth_client.post(
        "/api/v1/test-cases",
        json={"name": "Module Case", "project_id": project_id, "module": "billing"},
        headers=auth_headers,
    )
    resp = auth_client.get(
        f"/api/v1/test-cases?project_id={project_id}&module=billing",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    for item in data["data"]["items"]:
        assert item["module"] == "billing"


def test_list_test_cases_filter_by_priority(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    auth_client.post(
        "/api/v1/test-cases",
        json={"name": "Priority Case", "project_id": project_id, "priority": "P0"},
        headers=auth_headers,
    )
    resp = auth_client.get(
        f"/api/v1/test-cases?project_id={project_id}&priority=P0",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    for item in data["data"]["items"]:
        assert item["priority"] == "P0"


def test_list_test_cases_filter_by_status(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    create_resp = auth_client.post(
        "/api/v1/test-cases",
        json={"name": "Status Case", "project_id": project_id},
        headers=auth_headers,
    )
    case_id = create_resp.get_json()["data"]["id"]
    auth_client.put(
        f"/api/v1/test-cases/{case_id}",
        json={"status": "active"},
        headers=auth_headers,
    )
    resp = auth_client.get(
        f"/api/v1/test-cases?project_id={project_id}&status=active",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    for item in data["data"]["items"]:
        assert item["status"] == "active"


def test_get_test_case(auth_client, auth_headers, created_case):
    case_id = created_case["id"]
    resp = auth_client.get(
        f"/api/v1/test-cases/{case_id}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["data"]["id"] == case_id
    assert data["data"]["name"] == "Fixture Case"


def test_get_test_case_not_found(auth_client, auth_headers):
    resp = auth_client.get(
        "/api/v1/test-cases/99999",
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_update_test_case(auth_client, auth_headers, created_case):
    case_id = created_case["id"]
    resp = auth_client.put(
        f"/api/v1/test-cases/{case_id}",
        json={"name": "Updated Name", "module": "payments", "tags": ["e2e"], "priority": "P0", "status": "active"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["data"]["name"] == "Updated Name"
    assert data["data"]["module"] == "payments"
    assert data["data"]["tags"] == ["e2e"]
    assert data["data"]["priority"] == "P0"
    assert data["data"]["status"] == "active"


def test_update_test_case_not_found(auth_client, auth_headers):
    resp = auth_client.put(
        "/api/v1/test-cases/99999",
        json={"name": "Ghost"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_delete_test_case(auth_client, auth_headers, created_case):
    case_id = created_case["id"]
    resp = auth_client.delete(
        f"/api/v1/test-cases/{case_id}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    get_resp = auth_client.get(
        f"/api/v1/test-cases/{case_id}",
        headers=auth_headers,
    )
    assert get_resp.status_code == 404


def test_delete_test_case_not_found(auth_client, auth_headers):
    resp = auth_client.delete(
        "/api/v1/test-cases/99999",
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_get_modules(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    auth_client.post(
        "/api/v1/test-cases",
        json={"name": "M1", "project_id": project_id, "module": "auth"},
        headers=auth_headers,
    )
    auth_client.post(
        "/api/v1/test-cases",
        json={"name": "M2", "project_id": project_id, "module": "billing"},
        headers=auth_headers,
    )
    resp = auth_client.get(
        f"/api/v1/test-cases/modules?project_id={project_id}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "auth" in data["data"]
    assert "billing" in data["data"]


def test_get_modules_missing_project_id(auth_client, auth_headers):
    resp = auth_client.get(
        "/api/v1/test-cases/modules",
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_get_tags(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    auth_client.post(
        "/api/v1/test-cases",
        json={"name": "T1", "project_id": project_id, "tags": ["smoke", "api"]},
        headers=auth_headers,
    )
    auth_client.post(
        "/api/v1/test-cases",
        json={"name": "T2", "project_id": project_id, "tags": ["regression", "api"]},
        headers=auth_headers,
    )
    resp = auth_client.get(
        f"/api/v1/test-cases/tags?project_id={project_id}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["data"] == sorted(data["data"])
    assert "api" in data["data"]
    assert "smoke" in data["data"]
    assert "regression" in data["data"]


def test_get_tags_missing_project_id(auth_client, auth_headers):
    resp = auth_client.get(
        "/api/v1/test-cases/tags",
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_update_test_case_tags(auth_client, auth_headers, created_case):
    case_id = created_case["id"]
    resp = auth_client.put(
        f"/api/v1/test-cases/{case_id}/tags",
        json={"tags": ["new_tag", "updated_tag"]},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["data"]["tags"] == ["new_tag", "updated_tag"]


def test_update_test_case_tags_missing_tags(auth_client, auth_headers, created_case):
    case_id = created_case["id"]
    resp = auth_client.put(
        f"/api/v1/test-cases/{case_id}/tags",
        json={},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_update_test_case_tags_not_found(auth_client, auth_headers):
    resp = auth_client.put(
        "/api/v1/test-cases/99999/tags",
        json={"tags": ["x"]},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_copy_test_case(auth_client, auth_headers, created_case):
    case_id = created_case["id"]
    resp = auth_client.post(
        f"/api/v1/test-cases/{case_id}/copy",
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["data"]["name"] == "Fixture Case_副本"
    assert data["data"]["status"] == "draft"
    assert data["data"]["project_id"] == created_case["project_id"]
    assert data["data"]["id"] != case_id


def test_copy_test_case_not_found(auth_client, auth_headers):
    resp = auth_client.post(
        "/api/v1/test-cases/99999/copy",
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_export_test_cases(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    auth_client.post(
        "/api/v1/test-cases",
        json={"name": "Export Case", "project_id": project_id},
        headers=auth_headers,
    )
    resp = auth_client.get(
        f"/api/v1/test-cases/export?project_id={project_id}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1


def test_export_test_cases_yaml(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    auth_client.post(
        "/api/v1/test-cases",
        json={"name": "YAML Export Case", "project_id": project_id},
        headers=auth_headers,
    )
    resp = auth_client.get(
        f"/api/v1/test-cases/export?project_id={project_id}&format=yaml",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data["data"], str)


def test_export_test_cases_missing_project_id(auth_client, auth_headers):
    resp = auth_client.get(
        "/api/v1/test-cases/export",
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_import_test_cases(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    resp = auth_client.post(
        "/api/v1/test-cases/import",
        json={
            "project_id": project_id,
            "cases": [
                {"name": "Imported Case 1", "module": "import", "priority": "P1"},
                {"name": "Imported Case 2", "module": "import", "priority": "P2"},
            ],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert len(data["data"]) == 2
    assert data["data"][0]["name"] == "Imported Case 1"
    assert data["data"][1]["name"] == "Imported Case 2"
    assert data["data"][0]["status"] == "draft"


def test_import_test_cases_missing_project_id(auth_client, auth_headers):
    resp = auth_client.post(
        "/api/v1/test-cases/import",
        json={"cases": [{"name": "No Project"}]},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_import_test_cases_missing_cases(auth_client, auth_headers, test_project):
    project_id = test_project["id"]
    resp = auth_client.post(
        "/api/v1/test-cases/import",
        json={"project_id": project_id},
        headers=auth_headers,
    )
    assert resp.status_code == 400
