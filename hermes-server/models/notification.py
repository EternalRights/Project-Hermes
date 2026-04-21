from datetime import datetime, timezone

from hermes_server.app import db


class NotificationConfig(db.Model):
    __tablename__ = "notification_config"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    type = db.Column(db.Enum("webhook", "email", "wechat", "dingtalk", name="notification_type_enum"), nullable=False)
    config = db.Column(db.JSON)
    trigger_condition = db.Column(db.JSON)
    is_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    project = db.relationship("Project", backref=db.backref("notification_configs", lazy="dynamic"))
