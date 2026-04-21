from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_server.app import db
from hermes_server.app.response import success_response, error_response, paginate_response
from hermes_server.models.project import Project
from hermes_server.middleware.permission import require_permission

bp = Blueprint('projects', __name__, url_prefix='/api/v1/projects')


@bp.route('', methods=['GET'])
@jwt_required()
@require_permission('project:read')
def get_projects():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    name = request.args.get('name', '')

    query = Project.query.filter(Project.is_active == True)
    if name:
        query = query.filter(Project.name.ilike(f'%{name}%'))
    query = query.order_by(Project.created_at.desc())

    data = paginate_response(query, page, per_page)
    items = [item.to_dict() for item in data.pop('items')]
    return success_response(data={**data, 'items': items}), 200


@bp.route('', methods=['POST'])
@jwt_required()
@require_permission('project:create')
def create_project():
    user_id = get_jwt_identity()
    body = request.get_json(silent=True) or {}

    name = body.get('name')
    if not name:
        return error_response(message='name is required', code=400), 400

    description = body.get('description')

    project = Project(name=name, description=description, owner_id=user_id)
    db.session.add(project)
    db.session.commit()

    return success_response(data=project.to_dict(), message='created', code=201), 201


@bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
@require_permission('project:read')
def get_project(project_id):
    project = db.session.get(Project, project_id)
    if not project or not project.is_active:
        return error_response(message='project not found', code=404), 404

    return success_response(data=project.to_dict()), 200


@bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
@require_permission('project:update')
def update_project(project_id):
    project = db.session.get(Project, project_id)
    if not project or not project.is_active:
        return error_response(message='project not found', code=404), 404

    body = request.get_json(silent=True) or {}

    if 'name' in body:
        project.name = body['name']
    if 'description' in body:
        project.description = body['description']

    db.session.commit()

    return success_response(data=project.to_dict(), message='updated'), 200


@bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
@require_permission('project:delete')
def delete_project(project_id):
    project = db.session.get(Project, project_id)
    if not project or not project.is_active:
        return error_response(message='project not found', code=404), 404

    project.is_active = False
    db.session.commit()

    return success_response(message='deleted'), 200
