from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_worker.celery_app import celery_app
from hermes_server.services.execution_service import ExecutionService
from hermes_server.app.response import success_response, error_response, paginate_response
from hermes_server.app.error_handlers import HermesBusinessError
from hermes_server.middleware.permission import require_permission

bp = Blueprint('executions', __name__, url_prefix='/api/v1/executions')


@bp.route('', methods=['POST'])
@jwt_required()
@require_permission('execution:create')
def create_execution():
    data = request.get_json()
    if not data:
        return jsonify(error_response(message='request body is required')), 400

    current_user_id = get_jwt_identity()
    try:
        execution = ExecutionService.create_execution(data, current_user_id)

        celery_app.send_task(
            'hermes_worker.tasks.execute_test_suite',
            args=[execution.id, execution.suite_id, execution.environment_id],
        )

        return jsonify(success_response(data=execution.to_dict(), code=201)), 201
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:execution_id>', methods=['GET'])
@jwt_required()
@require_permission('execution:read')
def get_execution(execution_id):
    try:
        data = ExecutionService.get_execution_detail(execution_id)
        return jsonify(success_response(data=data))
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('', methods=['GET'])
@jwt_required()
@require_permission('execution:read')
def get_executions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    suite_id = request.args.get('suite_id', type=int)
    status = request.args.get('status', type=str)

    query = ExecutionService.list_executions(
        page=page, per_page=per_page, suite_id=suite_id, status=status,
    )
    result = paginate_response(query, page, per_page)
    items = [execution.to_dict() for execution in result['items']]
    result['items'] = items
    return jsonify(success_response(data=result))
