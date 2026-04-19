import pytest


@pytest.fixture()
def project(auth_client, auth_headers):
    resp = auth_client.post(
        "/api/v1/projects",
        json={"name": "Suite Test Project"},
        headers=auth_headers,
    )
    return resp.get_json()["data"]


@pytest.fixture()
def test_case(auth_client, auth_headers, project):
    resp = auth_client.post(
        "/api/v1/test-cases",
        json={
            "name": "Suite Test Case",
            "project_id": project["id"],
            "module": "auth",
            "priority": "P1",
            "request_config": {
                "method": "GET",
                "url": "http://localhost:5000/api/v1/projects",
                "headers": {"Content-Type": "application/json"},
            },
            "assertions": [{"type": "status_code", "expected": 200}],
        },
        headers=auth_headers,
    )
    return resp.get_json()["data"]


@pytest.fixture()
def second_test_case(auth_client, auth_headers, project):
    resp = auth_client.post(
        "/api/v1/test-cases",
        json={
            "name": "Suite Test Case 2",
            "project_id": project["id"],
            "module": "auth",
            "priority": "P2",
            "request_config": {
                "method": "POST",
                "url": "http://localhost:5000/api/v1/projects",
                "headers": {"Content-Type": "application/json"},
            },
            "assertions": [{"type": "status_code", "expected": 201}],
        },
        headers=auth_headers,
    )
    return resp.get_json()["data"]


@pytest.fixture()
def suite(auth_client, auth_headers, project):
    resp = auth_client.post(
        "/api/v1/test-suites",
        json={
            "name": "Fixture Suite",
            "project_id": project["id"],
            "description": "A fixture suite",
            "execution_mode": "serial",
        },
        headers=auth_headers,
    )
    return resp.get_json()["data"]


class TestCreateTestSuite:

    def test_create_success(self, auth_client, auth_headers, project):
        resp = auth_client.post(
            "/api/v1/test-suites",
            json={"name": "My Suite", "project_id": project["id"]},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 201
        assert data["code"] == 201
        assert data["data"]["name"] == "My Suite"
        assert data["data"]["project_id"] == project["id"]
        assert data["data"]["id"] is not None

    def test_create_missing_name(self, auth_client, auth_headers, project):
        resp = auth_client.post(
            "/api/v1/test-suites",
            json={"project_id": project["id"]},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 400
        assert data["code"] == 400

    def test_create_missing_project_id(self, auth_client, auth_headers):
        resp = auth_client.post(
            "/api/v1/test-suites",
            json={"name": "No Project Suite"},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 400
        assert data["code"] == 400

    def test_create_with_description_and_execution_mode(self, auth_client, auth_headers, project):
        resp = auth_client.post(
            "/api/v1/test-suites",
            json={
                "name": "Full Suite",
                "project_id": project["id"],
                "description": "Detailed description",
                "execution_mode": "parallel",
            },
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 201
        assert data["data"]["description"] == "Detailed description"
        assert data["data"]["execution_mode"] == "parallel"

    def test_create_default_execution_mode(self, auth_client, auth_headers, project):
        resp = auth_client.post(
            "/api/v1/test-suites",
            json={"name": "Default Mode Suite", "project_id": project["id"]},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 201
        assert data["data"]["execution_mode"] == "serial"


class TestListTestSuites:

    def test_list_returns_paginated_results(self, auth_client, auth_headers, project):
        for i in range(3):
            auth_client.post(
                "/api/v1/test-suites",
                json={"name": f"Suite {i}", "project_id": project["id"]},
                headers=auth_headers,
            )
        resp = auth_client.get(
            "/api/v1/test-suites",
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 200
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert "page" in data["data"]
        assert "per_page" in data["data"]
        assert data["data"]["total"] >= 3

    def test_list_filter_by_project_id(self, auth_client, auth_headers, project):
        other_resp = auth_client.post(
            "/api/v1/projects",
            json={"name": "Other Project"},
            headers=auth_headers,
        )
        other_project = other_resp.get_json()["data"]

        auth_client.post(
            "/api/v1/test-suites",
            json={"name": "Suite A", "project_id": project["id"]},
            headers=auth_headers,
        )
        auth_client.post(
            "/api/v1/test-suites",
            json={"name": "Suite B", "project_id": other_project["id"]},
            headers=auth_headers,
        )

        resp = auth_client.get(
            f"/api/v1/test-suites?project_id={project['id']}",
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 200
        for item in data["data"]["items"]:
            assert item["project_id"] == project["id"]


class TestGetTestSuite:

    def test_get_success_with_cases_list(self, auth_client, auth_headers, suite, test_case):
        auth_client.post(
            f"/api/v1/test-suites/{suite['id']}/cases",
            json={"case_id": test_case["id"]},
            headers=auth_headers,
        )
        resp = auth_client.get(
            f"/api/v1/test-suites/{suite['id']}",
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["data"]["id"] == suite["id"]
        assert data["data"]["name"] == suite["name"]
        assert "cases" in data["data"]
        assert len(data["data"]["cases"]) == 1
        assert data["data"]["cases"][0]["case_id"] == test_case["id"]

    def test_get_non_existent_returns_404(self, auth_client, auth_headers):
        resp = auth_client.get(
            "/api/v1/test-suites/99999",
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 404
        assert data["code"] == 404


class TestUpdateTestSuite:

    def test_update_name(self, auth_client, auth_headers, suite):
        resp = auth_client.put(
            f"/api/v1/test-suites/{suite['id']}",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["data"]["name"] == "Updated Name"

    def test_update_description(self, auth_client, auth_headers, suite):
        resp = auth_client.put(
            f"/api/v1/test-suites/{suite['id']}",
            json={"description": "New description"},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["data"]["description"] == "New description"

    def test_update_execution_mode(self, auth_client, auth_headers, suite):
        resp = auth_client.put(
            f"/api/v1/test-suites/{suite['id']}",
            json={"execution_mode": "parallel"},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["data"]["execution_mode"] == "parallel"

    def test_update_non_existent_returns_404(self, auth_client, auth_headers):
        resp = auth_client.put(
            "/api/v1/test-suites/99999",
            json={"name": "Ghost"},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 404
        assert data["code"] == 404


class TestDeleteTestSuite:

    def test_delete_success(self, auth_client, auth_headers, suite):
        resp = auth_client.delete(
            f"/api/v1/test-suites/{suite['id']}",
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["message"] == "deleted"

        get_resp = auth_client.get(
            f"/api/v1/test-suites/{suite['id']}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 404

    def test_delete_non_existent_returns_404(self, auth_client, auth_headers):
        resp = auth_client.delete(
            "/api/v1/test-suites/99999",
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 404
        assert data["code"] == 404


class TestAddCaseToSuite:

    def test_add_case_success(self, auth_client, auth_headers, suite, test_case):
        resp = auth_client.post(
            f"/api/v1/test-suites/{suite['id']}/cases",
            json={"case_id": test_case["id"]},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 201
        assert data["code"] == 201
        assert data["data"]["suite_id"] == suite["id"]
        assert data["data"]["case_id"] == test_case["id"]

    def test_add_case_missing_case_id(self, auth_client, auth_headers, suite):
        resp = auth_client.post(
            f"/api/v1/test-suites/{suite['id']}/cases",
            json={},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 400
        assert data["code"] == 400

    def test_add_non_existent_case_returns_404(self, auth_client, auth_headers, suite):
        resp = auth_client.post(
            f"/api/v1/test-suites/{suite['id']}/cases",
            json={"case_id": 99999},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 404
        assert data["code"] == 404

    def test_add_duplicate_case_returns_400(self, auth_client, auth_headers, suite, test_case):
        auth_client.post(
            f"/api/v1/test-suites/{suite['id']}/cases",
            json={"case_id": test_case["id"]},
            headers=auth_headers,
        )
        resp = auth_client.post(
            f"/api/v1/test-suites/{suite['id']}/cases",
            json={"case_id": test_case["id"]},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 400
        assert data["code"] == 400

    def test_add_case_non_existent_suite_returns_404(self, auth_client, auth_headers, test_case):
        resp = auth_client.post(
            "/api/v1/test-suites/99999/cases",
            json={"case_id": test_case["id"]},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 404
        assert data["code"] == 404


class TestRemoveCaseFromSuite:

    def test_remove_case_success(self, auth_client, auth_headers, suite, test_case):
        auth_client.post(
            f"/api/v1/test-suites/{suite['id']}/cases",
            json={"case_id": test_case["id"]},
            headers=auth_headers,
        )
        resp = auth_client.delete(
            f"/api/v1/test-suites/{suite['id']}/cases/{test_case['id']}",
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["message"] == "removed"

    def test_remove_non_existent_case_in_suite_returns_404(self, auth_client, auth_headers, suite):
        resp = auth_client.delete(
            f"/api/v1/test-suites/{suite['id']}/cases/99999",
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 404
        assert data["code"] == 404

    def test_remove_case_non_existent_suite_returns_404(self, auth_client, auth_headers, test_case):
        resp = auth_client.delete(
            f"/api/v1/test-suites/99999/cases/{test_case['id']}",
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 404
        assert data["code"] == 404


class TestReorderSuiteCases:

    def test_reorder_success(self, auth_client, auth_headers, suite, test_case, second_test_case):
        auth_client.post(
            f"/api/v1/test-suites/{suite['id']}/cases",
            json={"case_id": test_case["id"], "sort_order": 1},
            headers=auth_headers,
        )
        auth_client.post(
            f"/api/v1/test-suites/{suite['id']}/cases",
            json={"case_id": second_test_case["id"], "sort_order": 2},
            headers=auth_headers,
        )
        resp = auth_client.put(
            f"/api/v1/test-suites/{suite['id']}/cases/reorder",
            json={
                "orders": [
                    {"case_id": test_case["id"], "sort_order": 2},
                    {"case_id": second_test_case["id"], "sort_order": 1},
                ]
            },
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["message"] == "reordered"

        get_resp = auth_client.get(
            f"/api/v1/test-suites/{suite['id']}",
            headers=auth_headers,
        )
        cases = get_resp.get_json()["data"]["cases"]
        case_map = {c["case_id"]: c for c in cases}
        assert case_map[test_case["id"]]["sort_order"] == 2
        assert case_map[second_test_case["id"]]["sort_order"] == 1

    def test_reorder_missing_orders_returns_400(self, auth_client, auth_headers, suite):
        resp = auth_client.put(
            f"/api/v1/test-suites/{suite['id']}/cases/reorder",
            json={},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 400
        assert data["code"] == 400

    def test_reorder_non_existent_suite_returns_404(self, auth_client, auth_headers):
        resp = auth_client.put(
            "/api/v1/test-suites/99999/cases/reorder",
            json={"orders": []},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 404
        assert data["code"] == 404


class TestToggleSuiteCase:

    def test_toggle_success(self, auth_client, auth_headers, suite, test_case):
        auth_client.post(
            f"/api/v1/test-suites/{suite['id']}/cases",
            json={"case_id": test_case["id"]},
            headers=auth_headers,
        )
        resp = auth_client.put(
            f"/api/v1/test-suites/{suite['id']}/cases/{test_case['id']}/toggle",
            json={"is_enabled": False},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["data"]["is_enabled"] is False

    def test_toggle_missing_is_enabled_returns_400(self, auth_client, auth_headers, suite, test_case):
        auth_client.post(
            f"/api/v1/test-suites/{suite['id']}/cases",
            json={"case_id": test_case["id"]},
            headers=auth_headers,
        )
        resp = auth_client.put(
            f"/api/v1/test-suites/{suite['id']}/cases/{test_case['id']}/toggle",
            json={},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 400
        assert data["code"] == 400

    def test_toggle_non_existent_case_in_suite_returns_404(self, auth_client, auth_headers, suite):
        resp = auth_client.put(
            f"/api/v1/test-suites/{suite['id']}/cases/99999/toggle",
            json={"is_enabled": True},
            headers=auth_headers,
        )
        data = resp.get_json()
        assert resp.status_code == 404
        assert data["code"] == 404
