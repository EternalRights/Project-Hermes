from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_server.services.scheduled_task_service import ScheduledTaskService
from hermes_server.app.response import success_response, error_response, paginate_response
from hermes_server.app.error_handlers import HermesBusinessError
from hermes_server.middleware.permission import require_permission

bp = Blueprint('scheduled_tasks', __name__, url_prefix='/api/v1/scheduled-tasks')


@bp.route('', methods=['GET'])
@jwt_required()
@require_permission('scheduled_task:read')
def get_scheduled_tasks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    project_id = request.args.get('project_id', type=int)

    query = ScheduledTaskService.list_scheduled_tasks(page=page, per_page=per_page, project_id=project_id)
    data = paginate_response(query, page, per_page)
    items = [item.to_dict() for item in data.pop('items')]
    return jsonify(success_response(data={**data, 'items': items})), 200


@bp.route('', methods=['POST'])
@jwt_required()
@require_permission('scheduled_task:create')
def create_scheduled_task():
    user_id = get_jwt_identity()
    body = request.get_json(silent=True) or {}

    try:
        task = ScheduledTaskService.create_scheduled_task(body, user_id)
        return jsonify(success_response(data=task.to_dict(), message='created', code=201)), 201
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
@require_permission('scheduled_task:read')
def get_scheduled_task(task_id):
    try:
        task = ScheduledTaskService.get_scheduled_task(task_id)
        return jsonify(success_response(data=task.to_dict())), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
@require_permission('scheduled_task:update')
def update_scheduled_task(task_id):
    body = request.get_json(silent=True) or {}

    try:
        task = ScheduledTaskService.update_scheduled_task(task_id, body)
        return jsonify(success_response(data=task.to_dict(), message='updated')), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
@require_permission('scheduled_task:delete')
def delete_scheduled_task(task_id):
    try:
        ScheduledTaskService.delete_scheduled_task(task_id)
        return jsonify(success_response(message='deleted')), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:task_id>/toggle', methods=['PUT'])
@jwt_required()
@require_permission('scheduled_task:update')
def toggle_scheduled_task(task_id):
    body = request.get_json(silent=True) or {}
    is_enabled = body.get('is_enabled')
    if is_enabled is None:
        return jsonify(error_response(message='is_enabled is required', code=400)), 400

    try:
        task = ScheduledTaskService.toggle_scheduled_task(task_id, is_enabled)
        return jsonify(success_response(data=task.to_dict(), message='updated')), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:task_id>/history', methods=['GET'])
@jwt_required()
@require_permission('scheduled_task:read')
def get_scheduled_task_history(task_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    try:
        query = ScheduledTaskService.get_task_history(task_id, page=page, per_page=per_page)
        data = paginate_response(query, page, per_page)
        items = [item.to_dict() for item in data.pop('items')]
        return jsonify(success_response(data={**data, 'items': items})), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code
