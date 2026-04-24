from datetime import datetime, timezone

from hermes_server.app import db


class ScheduledTask(db.Model):
    __tablename__ = "scheduled_task"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    suite_id = db.Column(db.Integer, db.ForeignKey("test_suite.id"), nullable=False)
    environment_id = db.Column(db.Integer, db.ForeignKey("environment.id"), nullable=False)
    cron_expression = db.Column(db.String(128), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True)
    last_run_at = db.Column(db.DateTime)
    next_run_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    project = db.relationship("Project", backref=db.backref("scheduled_tasks", lazy="dynamic"))
    suite = db.relationship("TestSuite", backref=db.backref("scheduled_tasks", lazy="dynamic"))
    environment = db.relationship("Environment", backref=db.backref("scheduled_tasks", lazy="dynamic"))
    creator = db.relationship("User", backref=db.backref("created_scheduled_tasks", lazy="dynamic"))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'suite_id': self.suite_id,
            'environment_id': self.environment_id,
            'cron_expression': self.cron_expression,
            'is_enabled': self.is_enabled,
            'last_run_at': self.last_run_at.isoformat() if self.last_run_at else None,
            'next_run_at': self.next_run_at.isoformat() if self.next_run_at else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
