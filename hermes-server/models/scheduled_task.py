from datetime import datetime

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = db.relationship("Project", backref=db.backref("scheduled_tasks", lazy="dynamic"))
    suite = db.relationship("TestSuite", backref=db.backref("scheduled_tasks", lazy="dynamic"))
    environment = db.relationship("Environment", backref=db.backref("scheduled_tasks", lazy="dynamic"))
    creator = db.relationship("User", backref=db.backref("created_scheduled_tasks", lazy="dynamic"))
