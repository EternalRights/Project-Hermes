from datetime import datetime, timezone

from hermes_server.app import db


class Project(db.Model):
    __tablename__ = "project"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    owner = db.relationship("User", backref=db.backref("projects", lazy="dynamic"))
    environments = db.relationship("Environment", backref="project", lazy="dynamic")
    global_variables = db.relationship("GlobalVariable", backref="project", lazy="dynamic")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Environment(db.Model):
    __tablename__ = "environment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    base_url = db.Column(db.String(512))
    variables = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    global_variables = db.relationship("GlobalVariable", backref="environment", lazy="dynamic")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'base_url': self.base_url,
            'variables': self.variables,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class GlobalVariable(db.Model):
    __tablename__ = "global_variable"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(128), nullable=False)
    value = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    environment_id = db.Column(db.Integer, db.ForeignKey("environment.id"), nullable=True)
    description = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'project_id': self.project_id,
            'environment_id': self.environment_id,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
