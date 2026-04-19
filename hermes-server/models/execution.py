from datetime import datetime

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    plan = db.relationship("TestPlan", backref=db.backref("executions", lazy="dynamic"))
    suite = db.relationship("TestSuite", backref=db.backref("executions", lazy="dynamic"))
    environment = db.relationship("Environment", backref=db.backref("executions", lazy="dynamic"))
    creator = db.relationship("User", backref=db.backref("created_executions", lazy="dynamic"))
    step_results = db.relationship("TestStepResult", backref="execution", lazy="dynamic")


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
