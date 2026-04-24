from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_server.services.environment_service import EnvironmentService
from hermes_server.app.response import success_response, error_response, paginate_response
from hermes_server.app.error_handlers import HermesBusinessError
from hermes_server.middleware.permission import require_permission

bp = Blueprint('environments', __name__, url_prefix='/api/v1/projects/<int:project_id>/environments')


@bp.route('', methods=['GET'])
@jwt_required()
@require_permission('environment:read')
def get_environments(project_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        query = EnvironmentService.list_environments(project_id, page=page, per_page=per_page)
        data = paginate_response(query, page, per_page)
        items = [item.to_dict() for item in data.pop('items')]
        return jsonify(success_response(data={**data, 'items': items})), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('', methods=['POST'])
@jwt_required()
@require_permission('environment:create')
def create_environment(project_id):
    body = request.get_json(silent=True) or {}

    try:
        environment = EnvironmentService.create_environment(project_id, body)
        return jsonify(success_response(data=environment.to_dict(), message='created', code=201)), 201
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:environment_id>', methods=['GET'])
@jwt_required()
@require_permission('environment:read')
def get_environment(project_id, environment_id):
    try:
        environment = EnvironmentService.get_environment(project_id, environment_id)
        return jsonify(success_response(data=environment.to_dict())), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:environment_id>', methods=['PUT'])
@jwt_required()
@require_permission('environment:update')
def update_environment(project_id, environment_id):
    body = request.get_json(silent=True) or {}

    try:
        environment = EnvironmentService.update_environment(project_id, environment_id, body)
        return jsonify(success_response(data=environment.to_dict(), message='updated')), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:environment_id>', methods=['DELETE'])
@jwt_required()
@require_permission('environment:delete')
def delete_environment(project_id, environment_id):
    try:
        EnvironmentService.delete_environment(project_id, environment_id)
        return jsonify(success_response(message='deleted')), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code
