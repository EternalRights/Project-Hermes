from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_server.services.project_service import ProjectService
from hermes_server.app.response import success_response, error_response, paginate_response
from hermes_server.app.error_handlers import HermesBusinessError
from hermes_server.middleware.permission import require_permission

bp = Blueprint('projects', __name__, url_prefix='/api/v1/projects')


@bp.route('', methods=['GET'])
@jwt_required()
@require_permission('project:read')
def get_projects():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    name = request.args.get('name', '')

    query = ProjectService.list_projects(page=page, per_page=per_page, name=name)
    data = paginate_response(query, page, per_page)
    items = [item.to_dict() for item in data.pop('items')]
    return jsonify(success_response(data={**data, 'items': items})), 200


@bp.route('', methods=['POST'])
@jwt_required()
@require_permission('project:create')
def create_project():
    user_id = get_jwt_identity()
    body = request.get_json(silent=True) or {}

    try:
        project = ProjectService.create_project(
            name=body.get('name'),
            description=body.get('description'),
            owner_id=user_id,
        )
        return jsonify(success_response(data=project.to_dict(), message='created', code=201)), 201
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
@require_permission('project:read')
def get_project(project_id):
    try:
        project = ProjectService.get_project(project_id)
        return jsonify(success_response(data=project.to_dict())), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
@require_permission('project:update')
def update_project(project_id):
    body = request.get_json(silent=True) or {}
    try:
        project = ProjectService.update_project(
            project_id=project_id,
            name=body.get('name'),
            description=body.get('description'),
        )
        return jsonify(success_response(data=project.to_dict(), message='updated')), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
@require_permission('project:delete')
def delete_project(project_id):
    try:
        ProjectService.delete_project(project_id)
        return jsonify(success_response(message='deleted')), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code
