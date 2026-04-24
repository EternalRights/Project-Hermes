from hermes_server.app import db
from hermes_server.models.project import Project, Environment
from hermes_server.services.exceptions import ValidationError, NotFoundError


class EnvironmentService:
    @staticmethod
    def _get_active_project(project_id):
        project = db.session.get(Project, project_id)
        if not project or not project.is_active:
            raise NotFoundError('project not found')
        return project

    @staticmethod
    def list_environments(project_id, page=1, per_page=10):
        EnvironmentService._get_active_project(project_id)
        query = Environment.query.filter_by(project_id=project_id).order_by(Environment.created_at.desc())
        return query

    @staticmethod
    def create_environment(project_id, data):
        EnvironmentService._get_active_project(project_id)

        name = data.get('name')
        if not name:
            raise ValidationError('name is required')

        environment = Environment(
            name=name,
            project_id=project_id,
            base_url=data.get('base_url'),
            variables=data.get('variables'),
        )
        db.session.add(environment)
        db.session.commit()
        return environment

    @staticmethod
    def get_environment(project_id, environment_id):
        EnvironmentService._get_active_project(project_id)
        environment = Environment.query.filter_by(id=environment_id, project_id=project_id).first()
        if not environment:
            raise NotFoundError('environment not found')
        return environment

    @staticmethod
    def update_environment(project_id, environment_id, data):
        environment = EnvironmentService.get_environment(project_id, environment_id)

        if 'name' in data:
            environment.name = data['name']
        if 'base_url' in data:
            environment.base_url = data['base_url']
        if 'variables' in data:
            environment.variables = data['variables']

        db.session.commit()
        return environment

    @staticmethod
    def delete_environment(project_id, environment_id):
        environment = EnvironmentService.get_environment(project_id, environment_id)
        db.session.delete(environment)
        db.session.commit()
