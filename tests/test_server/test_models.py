import pytest

from app import db
from models.user import User, Role, Permission
from models.project import Project, Environment, GlobalVariable
from models.test_case import TestCase


class TestUserModel:
    def test_set_password_and_check_password_correct(self, client):
        with client.application.app_context():
            user = User(username="pwduser", email="pwd@example.com")
            user.set_password("secret123")
            db.session.add(user)
            db.session.commit()
            assert user.check_password("secret123") is True

    def test_check_password_wrong(self, client):
        with client.application.app_context():
            user = User(username="wrongpwd", email="wrong@example.com")
            user.set_password("secret123")
            db.session.add(user)
            db.session.commit()
            assert user.check_password("wrongpassword") is False

    def test_has_permission_true(self, client):
        with client.application.app_context():
            perm = Permission(name="Create Project", code="project:create")
            role = Role(name="admin_role", description="Admin")
            role.permissions.append(perm)
            user = User(username="permuser", email="perm@example.com")
            user.set_password("pass")
            user.roles.append(role)
            db.session.add(user)
            db.session.commit()
            assert user.has_permission("project:create") is True

    def test_has_permission_false(self, client):
        with client.application.app_context():
            perm = Permission(name="Create Project", code="project:create")
            role = Role(name="limited_role", description="Limited")
            role.permissions.append(perm)
            user = User(username="noperm", email="noperm@example.com")
            user.set_password("pass")
            user.roles.append(role)
            db.session.add(user)
            db.session.commit()
            assert user.has_permission("project:delete") is False


class TestProjectModel:
    def test_to_dict(self, client):
        with client.application.app_context():
            user = User(username="projowner", email="projowner@example.com")
            user.set_password("pass")
            db.session.add(user)
            db.session.commit()

            project = Project(name="TestProject", description="A test project", owner_id=user.id)
            db.session.add(project)
            db.session.commit()

            result = project.to_dict()
            assert result["id"] == project.id
            assert result["name"] == "TestProject"
            assert result["description"] == "A test project"
            assert result["owner_id"] == user.id
            assert result["is_active"] is True
            assert result["created_at"] is not None
            assert result["updated_at"] is not None


class TestEnvironmentModel:
    def test_to_dict(self, client):
        with client.application.app_context():
            user = User(username="envowner", email="envowner@example.com")
            user.set_password("pass")
            db.session.add(user)
            db.session.commit()

            project = Project(name="EnvProject", owner_id=user.id)
            db.session.add(project)
            db.session.commit()

            env = Environment(
                name="Staging",
                project_id=project.id,
                base_url="http://staging.example.com",
                variables={"API_KEY": "abc123"},
            )
            db.session.add(env)
            db.session.commit()

            result = env.to_dict()
            assert result["id"] == env.id
            assert result["name"] == "Staging"
            assert result["project_id"] == project.id
            assert result["base_url"] == "http://staging.example.com"
            assert result["variables"] == {"API_KEY": "abc123"}
            assert result["created_at"] is not None
            assert result["updated_at"] is not None


class TestTestCaseModel:
    def test_to_dict(self, client):
        with client.application.app_context():
            user = User(username="caseowner", email="caseowner@example.com")
            user.set_password("pass")
            db.session.add(user)
            db.session.commit()

            project = Project(name="CaseProject", owner_id=user.id)
            db.session.add(project)
            db.session.commit()

            request_config = {"method": "POST", "url": "/api/test", "headers": {"Content-Type": "application/json"}}
            assertions = [{"type": "status_code", "expected": 200}]
            pre_hooks = [{"type": "set_variable", "key": "token", "value": "abc"}]
            post_hooks = [{"type": "extract", "key": "id", "jsonpath": "$.data.id"}]
            variables = {"base_url": "http://localhost"}
            tags = ["smoke", "regression"]
            retry_config = {"max_retries": 3, "interval": 1000}

            test_case = TestCase(
                name="Login API Test",
                project_id=project.id,
                module="auth",
                tags=tags,
                priority="P1",
                status="active",
                request_config=request_config,
                assertions=assertions,
                pre_hooks=pre_hooks,
                post_hooks=post_hooks,
                variables=variables,
                retry_config=retry_config,
                timeout=5000,
                created_by=user.id,
            )
            db.session.add(test_case)
            db.session.commit()

            result = test_case.to_dict()
            assert result["id"] == test_case.id
            assert result["name"] == "Login API Test"
            assert result["project_id"] == project.id
            assert result["module"] == "auth"
            assert result["tags"] == tags
            assert result["priority"] == "P1"
            assert result["status"] == "active"
            assert result["request_config"] == request_config
            assert result["assertions"] == assertions
            assert result["pre_hooks"] == pre_hooks
            assert result["post_hooks"] == post_hooks
            assert result["variables"] == variables
            assert result["retry_config"] == retry_config
            assert result["timeout"] == 5000
            assert result["created_by"] == user.id
            assert result["created_at"] is not None
            assert result["updated_at"] is not None


class TestGlobalVariableModel:
    def test_to_dict(self, client):
        with client.application.app_context():
            user = User(username="varowner", email="varowner@example.com")
            user.set_password("pass")
            db.session.add(user)
            db.session.commit()

            project = Project(name="VarProject", owner_id=user.id)
            db.session.add(project)
            db.session.commit()

            env = Environment(name="Production", project_id=project.id, base_url="http://prod.example.com")
            db.session.add(env)
            db.session.commit()

            gvar = GlobalVariable(
                key="API_TOKEN",
                value="tok_abc123",
                project_id=project.id,
                environment_id=env.id,
                description="Production API token",
            )
            db.session.add(gvar)
            db.session.commit()

            result = gvar.to_dict()
            assert result["id"] == gvar.id
            assert result["key"] == "API_TOKEN"
            assert result["value"] == "tok_abc123"
            assert result["project_id"] == project.id
            assert result["environment_id"] == env.id
            assert result["description"] == "Production API token"
