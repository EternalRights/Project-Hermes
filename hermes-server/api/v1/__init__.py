from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')


def register_sub_blueprints():
    from api.v1 import auth
    from api.v1 import projects
    from api.v1 import environments
    from api.v1 import variables
    from api.v1 import test_cases
    from api.v1 import test_suites
    from api.v1 import executions
    from api.v1 import reports
    from api.v1 import scheduled_tasks
    from api.v1 import notifications
    from api.v1 import dashboard
    from api.v1 import health

    api_v1.register_blueprint(health.health_bp)
    api_v1.register_blueprint(auth.bp)
    api_v1.register_blueprint(projects.bp)
    api_v1.register_blueprint(environments.bp)
    api_v1.register_blueprint(variables.bp)
    api_v1.register_blueprint(test_cases.bp)
    api_v1.register_blueprint(test_suites.bp)
    api_v1.register_blueprint(executions.bp)
    api_v1.register_blueprint(reports.bp)
    api_v1.register_blueprint(scheduled_tasks.bp)
    api_v1.register_blueprint(notifications.bp)
    api_v1.register_blueprint(dashboard.dashboard_bp)


register_sub_blueprints()
