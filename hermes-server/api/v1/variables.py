from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_server.services.variable_service import VariableService
from hermes_server.app.response import success_response, error_response, paginate_response
from hermes_server.app.error_handlers import HermesBusinessError
from hermes_server.middleware.permission import require_permission

bp = Blueprint('variables', __name__, url_prefix='/api/v1/projects/<int:project_id>/variables')


@bp.route('', methods=['GET'])
@jwt_required()
@require_permission('variable:read')
def get_variables(project_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    environment_id = request.args.get('environment_id', None, type=int)

    try:
        query = VariableService.list_variables(project_id, page=page, per_page=per_page, environment_id=environment_id)
        data = paginate_response(query, page, per_page)
        items = [item.to_dict() for item in data.pop('items')]
        return jsonify(success_response(data={**data, 'items': items})), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('', methods=['POST'])
@jwt_required()
@require_permission('variable:create')
def create_variable(project_id):
    body = request.get_json(silent=True) or {}

    try:
        variable = VariableService.create_variable(project_id, body)
        return jsonify(success_response(data=variable.to_dict(), message='created', code=201)), 201
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:variable_id>', methods=['PUT'])
@jwt_required()
@require_permission('variable:update')
def update_variable(project_id, variable_id):
    body = request.get_json(silent=True) or {}

    try:
        variable = VariableService.update_variable(project_id, variable_id, body)
        return jsonify(success_response(data=variable.to_dict(), message='updated')), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:variable_id>', methods=['DELETE'])
@jwt_required()
@require_permission('variable:delete')
def delete_variable(project_id, variable_id):
    try:
        VariableService.delete_variable(project_id, variable_id)
        return jsonify(success_response(message='deleted')), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code
