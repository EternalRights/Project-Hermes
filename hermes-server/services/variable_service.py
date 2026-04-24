from hermes_server.app import db
from hermes_server.models.project import Project, GlobalVariable
from hermes_server.services.exceptions import ValidationError, NotFoundError


class VariableService:
    @staticmethod
    def _get_active_project(project_id):
        project = db.session.get(Project, project_id)
        if not project or not project.is_active:
            raise NotFoundError('project not found')
        return project

    @staticmethod
    def list_variables(project_id, page=1, per_page=10, environment_id=None):
        VariableService._get_active_project(project_id)
        query = GlobalVariable.query.filter_by(project_id=project_id)
        if environment_id is not None:
            query = query.filter_by(environment_id=environment_id)
        query = query.order_by(GlobalVariable.created_at.desc())
        return query

    @staticmethod
    def create_variable(project_id, data):
        VariableService._get_active_project(project_id)

        key = data.get('key')
        if not key:
            raise ValidationError('key is required')

        variable = GlobalVariable(
            key=key,
            value=data.get('value'),
            project_id=project_id,
            environment_id=data.get('environment_id'),
            description=data.get('description'),
        )
        db.session.add(variable)
        db.session.commit()
        return variable

    @staticmethod
    def get_variable(project_id, variable_id):
        VariableService._get_active_project(project_id)
        variable = GlobalVariable.query.filter_by(id=variable_id, project_id=project_id).first()
        if not variable:
            raise NotFoundError('variable not found')
        return variable

    @staticmethod
    def update_variable(project_id, variable_id, data):
        variable = VariableService.get_variable(project_id, variable_id)

        if 'key' in data:
            variable.key = data['key']
        if 'value' in data:
            variable.value = data['value']
        if 'environment_id' in data:
            variable.environment_id = data['environment_id']
        if 'description' in data:
            variable.description = data['description']

        db.session.commit()
        return variable

    @staticmethod
    def delete_variable(project_id, variable_id):
        variable = VariableService.get_variable(project_id, variable_id)
        db.session.delete(variable)
        db.session.commit()
