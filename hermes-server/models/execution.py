from datetime import datetime, timezone

from hermes_server.app import db


class TestExecution(db.Model):
    __tablename__ = "test_execution"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("test_plan.id"), nullable=True)
    suite_id = db.Column(db.Integer, db.ForeignKey("test_suite.id"), nullable=False)
    environment_id = db.Column(db.Integer, db.ForeignKey("environment.id"), nullable=False)
    status = db.Column(db.Enum("pending", "running", "success", "failed", "error", name="execution_status_enum"), default="pending")
    total_count = db.Column(db.Integer, default=0)
    pass_count = db.Column(db.Integer, default=0)
    fail_count = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)
    skip_count = db.Column(db.Integer, default=0)
    duration = db.Column(db.Float, default=0.0)
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    plan = db.relationship("TestPlan", backref=db.backref("executions", lazy="dynamic"))
    suite = db.relationship("TestSuite", backref=db.backref("executions", lazy="dynamic"))
    environment = db.relationship("Environment", backref=db.backref("executions", lazy="dynamic"))
    creator = db.relationship("User", backref=db.backref("created_executions", lazy="dynamic"))
    step_results = db.relationship("TestStepResult", backref="execution", lazy="dynamic")

    def to_dict(self, include_steps=False):
        data = {
            'id': self.id,
            'plan_id': self.plan_id,
            'suite_id': self.suite_id,
            'environment_id': self.environment_id,
            'status': self.status,
            'total_count': self.total_count,
            'pass_count': self.pass_count,
            'fail_count': self.fail_count,
            'error_count': self.error_count,
            'skip_count': self.skip_count,
            'duration': self.duration,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_steps:
            data['step_results'] = [s.to_dict() for s in self.step_results.order_by(TestStepResult.id.asc()).all()]
        return data


class TestStepResult(db.Model):
    __tablename__ = "test_step_result"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    execution_id = db.Column(db.Integer, db.ForeignKey("test_execution.id"), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey("test_case.id"), nullable=False)
    case_name = db.Column(db.String(128), nullable=False)
    status = db.Column(db.Enum("pending", "running", "pass", "fail", "error", "skip", name="step_status_enum"), default="pending")
    request_config = db.Column(db.JSON)
    response_status_code = db.Column(db.Integer)
    response_headers = db.Column(db.JSON)
    response_body = db.Column(db.Text)
    response_time = db.Column(db.Float, default=0.0)
    assertions_result = db.Column(db.JSON)
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)

    test_case = db.relationship("TestCase", backref=db.backref("step_results", lazy="dynamic"))

    def to_dict(self):
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'case_id': self.case_id,
            'case_name': self.case_name,
            'status': self.status,
            'request_config': self.request_config,
            'response_status_code': self.response_status_code,
            'response_headers': self.response_headers,
            'response_body': self.response_body,
            'response_time': self.response_time,
            'assertions_result': self.assertions_result,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
        }
