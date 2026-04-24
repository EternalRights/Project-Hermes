from datetime import datetime, timezone

from hermes_server.app import db


class TestCase(db.Model):
    __tablename__ = "test_case"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    module = db.Column(db.String(128))
    tags = db.Column(db.JSON)
    priority = db.Column(db.Enum("P0", "P1", "P2", "P3", name="priority_enum"), default="P2")
    status = db.Column(db.Enum("draft", "active", "disabled", name="case_status_enum"), default="draft")
    request_config = db.Column(db.JSON)
    assertions = db.Column(db.JSON)
    pre_hooks = db.Column(db.JSON)
    post_hooks = db.Column(db.JSON)
    variables = db.Column(db.JSON)
    data_source_id = db.Column(db.Integer, db.ForeignKey("data_source.id"), nullable=True)
    retry_config = db.Column(db.JSON)
    timeout = db.Column(db.Integer, default=30000)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    project = db.relationship("Project", backref=db.backref("test_cases", lazy="dynamic"))
    creator = db.relationship("User", backref=db.backref("created_test_cases", lazy="dynamic"))
    data_source = db.relationship("DataSource", backref=db.backref("test_cases", lazy="dynamic"))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'module': self.module,
            'tags': self.tags,
            'priority': self.priority,
            'status': self.status,
            'request_config': self.request_config,
            'assertions': self.assertions,
            'pre_hooks': self.pre_hooks,
            'post_hooks': self.post_hooks,
            'variables': self.variables,
            'data_source_id': self.data_source_id,
            'retry_config': self.retry_config,
            'timeout': self.timeout,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class TestSuite(db.Model):
    __tablename__ = "test_suite"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    description = db.Column(db.Text)
    execution_mode = db.Column(db.Enum("serial", "parallel", name="execution_mode_enum"), default="serial")
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    project = db.relationship("Project", backref=db.backref("test_suites", lazy="dynamic"))
    creator = db.relationship("User", backref=db.backref("created_test_suites", lazy="dynamic"))
    suite_cases = db.relationship("TestSuiteCase", backref="suite", lazy="dynamic")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'description': self.description,
            'execution_mode': self.execution_mode,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class TestSuiteCase(db.Model):
    __tablename__ = "test_suite_case"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    suite_id = db.Column(db.Integer, db.ForeignKey("test_suite.id"), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey("test_case.id"), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    is_enabled = db.Column(db.Boolean, default=True)

    test_case = db.relationship("TestCase", backref=db.backref("suite_entries", lazy="dynamic"))

    def to_dict(self):
        result = {
            'id': self.id,
            'suite_id': self.suite_id,
            'case_id': self.case_id,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
        }
        if self.test_case:
            result['test_case'] = self.test_case.to_dict()
        return result


class TestPlan(db.Model):
    __tablename__ = "test_plan"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    suite_id = db.Column(db.Integer, db.ForeignKey("test_suite.id"), nullable=False)
    environment_id = db.Column(db.Integer, db.ForeignKey("environment.id"), nullable=False)
    schedule_config = db.Column(db.JSON)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    project = db.relationship("Project", backref=db.backref("test_plans", lazy="dynamic"))
    suite = db.relationship("TestSuite", backref=db.backref("test_plans", lazy="dynamic"))
    environment = db.relationship("Environment", backref=db.backref("test_plans", lazy="dynamic"))
    creator = db.relationship("User", backref=db.backref("created_test_plans", lazy="dynamic"))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'suite_id': self.suite_id,
            'environment_id': self.environment_id,
            'schedule_config': self.schedule_config,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
