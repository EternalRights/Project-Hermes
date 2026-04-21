from hermes_server.app import create_app, db
from hermes_server.models.user import User, Role, Permission
import logging

logger = logging.getLogger(__name__)


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        roles_data = [
            {"name": "admin", "description": "System Administrator"},
            {"name": "test_manager", "description": "Test Manager"},
            {"name": "test_engineer", "description": "Test Engineer"},
            {"name": "viewer", "description": "Viewer"},
        ]
        roles = {}
        for r in roles_data:
            role = Role.query.filter_by(name=r["name"]).first()
            if not role:
                role = Role(name=r["name"], description=r["description"])
                db.session.add(role)
            roles[r["name"]] = role

        permissions_data = [
            {"name": "Create Test Case", "code": "test_case:create"},
            {"name": "Read Test Case", "code": "test_case:read"},
            {"name": "Update Test Case", "code": "test_case:update"},
            {"name": "Delete Test Case", "code": "test_case:delete"},
            {"name": "Create Test Suite", "code": "test_suite:create"},
            {"name": "Read Test Suite", "code": "test_suite:read"},
            {"name": "Update Test Suite", "code": "test_suite:update"},
            {"name": "Delete Test Suite", "code": "test_suite:delete"},
            {"name": "Create Execution", "code": "execution:create"},
            {"name": "Read Execution", "code": "execution:read"},
            {"name": "Manage Project", "code": "project:manage"},
            {"name": "Manage User", "code": "user:manage"},
        ]
        permissions = {}
        for p in permissions_data:
            perm = Permission.query.filter_by(code=p["code"]).first()
            if not perm:
                perm = Permission(name=p["name"], code=p["code"])
                db.session.add(perm)
            permissions[p["code"]] = perm

        db.session.flush()

        admin_role = roles["admin"]
        for perm in permissions.values():
            if not admin_role.permissions.filter_by(id=perm.id).first():
                admin_role.permissions.append(perm)

        admin_user = User.query.filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(username="admin", email="admin@hermes.local", is_active=True)
            admin_user.set_password("admin123")
            db.session.add(admin_user)
            logger.warning("Default admin user created with default password 'admin123'. Please change it immediately.")

        db.session.flush()

        if not admin_user.roles.filter_by(id=admin_role.id).first():
            admin_user.roles.append(admin_role)

        db.session.commit()
        print("Seed data created successfully.")


if __name__ == "__main__":
    seed()
