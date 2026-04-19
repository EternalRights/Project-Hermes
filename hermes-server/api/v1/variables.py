from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_server.app import db
from hermes_server.app.response import success_response, error_response, paginate_response
from hermes_server.models.project import Project, GlobalVariable

bp = Blueprint('variables', __name__, url_prefix='/api/v1/projects/<int:project_id>/variables')


@bp.route('', methods=['GET'])
@jwt_required()
def get_variables(project_id):
    project = Project.query.get(project_id)
    if not project or not project.is_active:
        return error_response(message='project not found', code=404), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    environment_id = request.args.get('environment_id', None, type=int)

    query = GlobalVariable.query.filter_by(project_id=project_id)
    if environment_id is not None:
        query = query.filter_by(environment_id=environment_id)
    query = query.order_by(GlobalVariable.created_at.desc())

    data = paginate_response(query, page, per_page)
    items = [item.to_dict() for item in data.pop('items')]
    return success_response(data={**data, 'items': items}), 200


@bp.route('', methods=['POST'])
@jwt_required()
def create_variable(project_id):
    project = Project.query.get(project_id)
    if not project or not project.is_active:
        return error_response(message='project not found', code=404), 404

    body = request.get_json(silent=True) or {}

    key = body.get('key')
    if not key:
        return error_response(message='key is required', code=400), 400

    value = body.get('value')
    environment_id = body.get('environment_id')
    description = body.get('description')

    variable = GlobalVariable(key=key, value=value, project_id=project_id, environment_id=environment_id, description=description)
    db.session.add(variable)
    db.session.commit()

    return success_response(data=variable.to_dict(), message='created', code=201), 201


@bp.route('/<int:variable_id>', methods=['PUT'])
@jwt_required()
def update_variable(project_id, variable_id):
    project = Project.query.get(project_id)
    if not project or not project.is_active:
        return error_response(message='project not found', code=404), 404

    variable = GlobalVariable.query.filter_by(id=variable_id, project_id=project_id).first()
    if not variable:
        return error_response(message='variable not found', code=404), 404

    body = request.get_json(silent=True) or {}

    if 'key' in body:
        variable.key = body['key']
    if 'value' in body:
        variable.value = body['value']
    if 'environment_id' in body:
        variable.environment_id = body['environment_id']
    if 'description' in body:
        variable.description = body['description']

    db.session.commit()

    return success_response(data=variable.to_dict(), message='updated'), 200


@bp.route('/<int:variable_id>', methods=['DELETE'])
@jwt_required()
def delete_variable(project_id, variable_id):
    project = Project.query.get(project_id)
    if not project or not project.is_active:
        return error_response(message='project not found', code=404), 404

    variable = GlobalVariable.query.filter_by(id=variable_id, project_id=project_id).first()
    if not variable:
        return error_response(message='variable not found', code=404), 404

    db.session.delete(variable)
    db.session.commit()

    return success_response(message='deleted'), 200
