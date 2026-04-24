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

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'type': self.type,
            'config': self.config,
            'trigger_condition': self.trigger_condition,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
