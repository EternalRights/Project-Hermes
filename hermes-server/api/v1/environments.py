from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_server.app import db
from hermes_server.app.response import success_response, error_response, paginate_response
from hermes_server.models.project import Project, Environment
from hermes_server.middleware.permission import require_permission

bp = Blueprint('environments', __name__, url_prefix='/api/v1/projects/<int:project_id>/environments')


@bp.route('', methods=['GET'])
@jwt_required()
@require_permission('environment:read')
def get_environments(project_id):
    project = db.session.get(Project, project_id)
    if not project or not project.is_active:
        return error_response(message='project not found', code=404), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Environment.query.filter_by(project_id=project_id).order_by(Environment.created_at.desc())

    data = paginate_response(query, page, per_page)
    items = [item.to_dict() for item in data.pop('items')]
    return success_response(data={**data, 'items': items}), 200


@bp.route('', methods=['POST'])
@jwt_required()
@require_permission('environment:create')
def create_environment(project_id):
    project = db.session.get(Project, project_id)
    if not project or not project.is_active:
        return error_response(message='project not found', code=404), 404

    body = request.get_json(silent=True) or {}

    name = body.get('name')
    if not name:
        return error_response(message='name is required', code=400), 400

    base_url = body.get('base_url')
    variables = body.get('variables')

    environment = Environment(name=name, project_id=project_id, base_url=base_url, variables=variables)
    db.session.add(environment)
    db.session.commit()

    return success_response(data=environment.to_dict(), message='created', code=201), 201


@bp.route('/<int:environment_id>', methods=['GET'])
@jwt_required()
@require_permission('environment:read')
def get_environment(project_id, environment_id):
    project = db.session.get(Project, project_id)
    if not project or not project.is_active:
        return error_response(message='project not found', code=404), 404

    environment = Environment.query.filter_by(id=environment_id, project_id=project_id).first()
    if not environment:
        return error_response(message='environment not found', code=404), 404

    return success_response(data=environment.to_dict()), 200


@bp.route('/<int:environment_id>', methods=['PUT'])
@jwt_required()
@require_permission('environment:update')
def update_environment(project_id, environment_id):
    project = db.session.get(Project, project_id)
    if not project or not project.is_active:
        return error_response(message='project not found', code=404), 404

    environment = Environment.query.filter_by(id=environment_id, project_id=project_id).first()
    if not environment:
        return error_response(message='environment not found', code=404), 404

    body = request.get_json(silent=True) or {}

    if 'name' in body:
        environment.name = body['name']
    if 'base_url' in body:
        environment.base_url = body['base_url']
    if 'variables' in body:
        environment.variables = body['variables']

    db.session.commit()

    return success_response(data=environment.to_dict(), message='updated'), 200


@bp.route('/<int:environment_id>', methods=['DELETE'])
@jwt_required()
@require_permission('environment:delete')
def delete_environment(project_id, environment_id):
    project = db.session.get(Project, project_id)
    if not project or not project.is_active:
        return error_response(message='project not found', code=404), 404

    environment = Environment.query.filter_by(id=environment_id, project_id=project_id).first()
    if not environment:
        return error_response(message='environment not found', code=404), 404

    db.session.delete(environment)
    db.session.commit()

    return success_response(message='deleted'), 200
