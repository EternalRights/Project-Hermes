from datetime import datetime

import pytest

from hermes_server.app import db
from hermes_server.models.project import Project, Environment
from hermes_server.models.test_case import TestCase, TestSuite
from hermes_server.models.execution import TestExecution, TestStepResult
from hermes_server.models.user import User


@pytest.fixture()
def report_data(auth_client, auth_headers):
    with auth_client.application.app_context():
        user = User.query.first()
        if not user:
            user = User(username="reportuser", email="report@example.com", password_hash="hash")
            db.session.add(user)
            db.session.flush()

        project = Project(name="Report Project", description="For reports", owner_id=user.id)
        db.session.add(project)
        db.session.flush()

        env = Environment(name="Report Env", project_id=project.id, base_url="http://localhost:5000")
        db.session.add(env)
        db.session.flush()

        test_case = TestCase(
            name="Report Case 1", project_id=project.id, created_by=user.id,
            module="auth", priority="P1", status="active",
        )
        db.session.add(test_case)
        db.session.flush()

        suite = TestSuite(name="Report Suite", project_id=project.id, created_by=user.id)
        db.session.add(suite)
        db.session.flush()

        execution = TestExecution(
            suite_id=suite.id,
            environment_id=env.id,
            status="success",
            total_count=3,
            pass_count=2,
            fail_count=1,
            error_count=0,
            skip_count=0,
            duration=1.5,
            started_at=datetime(2025, 1, 1, 10, 0, 0),
            finished_at=datetime(2025, 1, 1, 10, 0, 1),
            created_by=user.id,
        )
        db.session.add(execution)
        db.session.flush()

        step1 = TestStepResult(
            execution_id=execution.id,
            case_id=test_case.id,
            case_name="Step Pass 1",
            status="pass",
            response_status_code=200,
            response_time=100.0,
            assertions_result=[{"type": "status_code", "expected": 200, "actual": 200, "passed": True}],
            started_at=datetime(2025, 1, 1, 10, 0, 0),
            finished_at=datetime(2025, 1, 1, 10, 0, 0, 1),
        )
        step2 = TestStepResult(
            execution_id=execution.id,
            case_id=test_case.id,
            case_name="Step Pass 2",
            status="pass",
            response_status_code=200,
            response_time=200.0,
            assertions_result=[{"type": "status_code", "expected": 200, "actual": 200, "passed": True}],
            started_at=datetime(2025, 1, 1, 10, 0, 0, 1),
            finished_at=datetime(2025, 1, 1, 10, 0, 0, 2),
        )
        step3 = TestStepResult(
            execution_id=execution.id,
            case_id=test_case.id,
            case_name="Step Fail 1",
            status="fail",
            response_status_code=500,
            response_time=300.0,
            error_message="Internal Server Error",
            assertions_result=[{"type": "status_code", "expected": 200, "actual": 500, "passed": False}],
            started_at=datetime(2025, 1, 1, 10, 0, 0, 2),
            finished_at=datetime(2025, 1, 1, 10, 0, 0, 3),
        )
        db.session.add_all([step1, step2, step3])
        db.session.commit()

        return {
            "project_id": project.id,
            "environment_id": env.id,
            "suite_id": suite.id,
            "execution_id": execution.id,
            "test_case_id": test_case.id,
        }


def test_get_report(auth_client, auth_headers, report_data):
    execution_id = report_data["execution_id"]
    resp = auth_client.get(f"/api/v1/reports/{execution_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    summary = data["summary"]
    assert summary["pass_rate"] == 66.67
    assert summary["fail_rate"] == 33.33
    assert summary["avg_response_time"] == 200.0
    assert summary["p95_response_time"] == 300.0
    assert summary["p99_response_time"] == 300.0
    assert summary["total_count"] == 3
    assert summary["pass_count"] == 2
    assert summary["fail_count"] == 1
    assert len(data["step_results"]) == 3
    assert len(data["failed_cases"]) == 1
    assert data["failed_cases"][0]["case_name"] == "Step Fail 1"


def test_get_report_not_found(auth_client, auth_headers, report_data):
    resp = auth_client.get("/api/v1/reports/99999", headers=auth_headers)
    assert resp.status_code == 404


def test_get_trend(auth_client, auth_headers, report_data):
    suite_id = report_data["suite_id"]
    resp = auth_client.get(f"/api/v1/reports/trend?suite_id={suite_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "pass_rate_trend" in data
    assert "avg_response_time_trend" in data
    assert len(data["pass_rate_trend"]) >= 1
    assert len(data["avg_response_time_trend"]) >= 1


def test_get_trend_missing_suite_id(auth_client, auth_headers, report_data):
    resp = auth_client.get("/api/v1/reports/trend", headers=auth_headers)
    assert resp.status_code == 400


def test_export_report(auth_client, auth_headers, report_data):
    execution_id = report_data["execution_id"]
    resp = auth_client.get(f"/api/v1/reports/{execution_id}/export", headers=auth_headers)
    assert resp.status_code == 200
    assert "text/html" in resp.content_type
    html = resp.data.decode("utf-8")
    assert f"Execution #{execution_id}" in html
    assert "Step Pass 1" in html
    assert "Step Fail 1" in html


def test_export_report_not_found(auth_client, auth_headers, report_data):
    resp = auth_client.get("/api/v1/reports/99999/export", headers=auth_headers)
    assert resp.status_code == 404
