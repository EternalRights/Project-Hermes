from datetime import datetime, timezone

from hermes_server.app import db


class DataSource(db.Model):
    __tablename__ = "data_source"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    type = db.Column(db.Enum("csv", "json", "database", name="data_source_type_enum"), nullable=False)
    config = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    project = db.relationship("Project", backref=db.backref("data_sources", lazy="dynamic"))
