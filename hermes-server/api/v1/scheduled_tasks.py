from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_server.app import db
from hermes_server.app.response import success_response, error_response, paginate_response
from hermes_server.models.scheduled_task import ScheduledTask
from hermes_server.models.execution import TestExecution
from hermes_server.middleware.permission import require_permission

bp = Blueprint('scheduled_tasks', __name__, url_prefix='/api/v1/scheduled-tasks')


@bp.route('', methods=['GET'])
@jwt_required()
@require_permission('scheduled_task:read')
def get_scheduled_tasks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    project_id = request.args.get('project_id', type=int)

    query = ScheduledTask.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    query = query.order_by(ScheduledTask.created_at.desc())

    data = paginate_response(query, page, per_page)
    items = []
    for item in data.pop('items'):
        items.append({
            'id': item.id,
            'name': item.name,
            'project_id': item.project_id,
            'suite_id': item.suite_id,
            'environment_id': item.environment_id,
            'cron_expression': item.cron_expression,
            'is_enabled': item.is_enabled,
            'last_run_at': item.last_run_at.isoformat() if item.last_run_at else None,
            'next_run_at': item.next_run_at.isoformat() if item.next_run_at else None,
            'created_by': item.created_by,
            'created_at': item.created_at.isoformat() if item.created_at else None,
            'updated_at': item.updated_at.isoformat() if item.updated_at else None,
        })

    return success_response(data={**data, 'items': items}), 200


@bp.route('', methods=['POST'])
@jwt_required()
@require_permission('scheduled_task:create')
def create_scheduled_task():
    user_id = get_jwt_identity()
    body = request.get_json(silent=True) or {}

    name = body.get('name')
    project_id = body.get('project_id')
    suite_id = body.get('suite_id')
    environment_id = body.get('environment_id')
    cron_expression = body.get('cron_expression')

    if not all([name, project_id, suite_id, environment_id, cron_expression]):
        return error_response(message='name, project_id, suite_id, environment_id, cron_expression are required', code=400), 400

    task = ScheduledTask(
        name=name,
        project_id=project_id,
        suite_id=suite_id,
        environment_id=environment_id,
        cron_expression=cron_expression,
        created_by=user_id,
    )
    db.session.add(task)
    db.session.commit()

    return success_response(data={
        'id': task.id,
        'name': task.name,
        'project_id': task.project_id,
        'suite_id': task.suite_id,
        'environment_id': task.environment_id,
        'cron_expression': task.cron_expression,
        'is_enabled': task.is_enabled,
        'created_by': task.created_by,
        'created_at': task.created_at.isoformat() if task.created_at else None,
    }, message='created', code=201), 201


@bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
@require_permission('scheduled_task:read')
def get_scheduled_task(task_id):
    task = db.session.get(ScheduledTask, task_id)
    if not task:
        return error_response(message='scheduled task not found', code=404), 404

    return success_response(data={
        'id': task.id,
        'name': task.name,
        'project_id': task.project_id,
        'suite_id': task.suite_id,
        'environment_id': task.environment_id,
        'cron_expression': task.cron_expression,
        'is_enabled': task.is_enabled,
        'last_run_at': task.last_run_at.isoformat() if task.last_run_at else None,
        'next_run_at': task.next_run_at.isoformat() if task.next_run_at else None,
        'created_by': task.created_by,
        'created_at': task.created_at.isoformat() if task.created_at else None,
        'updated_at': task.updated_at.isoformat() if task.updated_at else None,
    }), 200


@bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
@require_permission('scheduled_task:update')
def update_scheduled_task(task_id):
    task = db.session.get(ScheduledTask, task_id)
    if not task:
        return error_response(message='scheduled task not found', code=404), 404

    body = request.get_json(silent=True) or {}

    if 'name' in body:
        task.name = body['name']
    if 'project_id' in body:
        task.project_id = body['project_id']
    if 'suite_id' in body:
        task.suite_id = body['suite_id']
    if 'environment_id' in body:
        task.environment_id = body['environment_id']
    if 'cron_expression' in body:
        task.cron_expression = body['cron_expression']

    db.session.commit()

    return success_response(data={
        'id': task.id,
        'name': task.name,
        'project_id': task.project_id,
        'suite_id': task.suite_id,
        'environment_id': task.environment_id,
        'cron_expression': task.cron_expression,
        'is_enabled': task.is_enabled,
        'last_run_at': task.last_run_at.isoformat() if task.last_run_at else None,
        'next_run_at': task.next_run_at.isoformat() if task.next_run_at else None,
        'created_by': task.created_by,
        'created_at': task.created_at.isoformat() if task.created_at else None,
        'updated_at': task.updated_at.isoformat() if task.updated_at else None,
    }, message='updated'), 200


@bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
@require_permission('scheduled_task:delete')
def delete_scheduled_task(task_id):
    task = db.session.get(ScheduledTask, task_id)
    if not task:
        return error_response(message='scheduled task not found', code=404), 404

    db.session.delete(task)
    db.session.commit()

    return success_response(message='deleted'), 200


@bp.route('/<int:task_id>/toggle', methods=['PUT'])
@jwt_required()
@require_permission('scheduled_task:update')
def toggle_scheduled_task(task_id):
    task = db.session.get(ScheduledTask, task_id)
    if not task:
        return error_response(message='scheduled task not found', code=404), 404

    body = request.get_json(silent=True) or {}
    is_enabled = body.get('is_enabled')
    if is_enabled is None:
        return error_response(message='is_enabled is required', code=400), 400

    task.is_enabled = is_enabled
    db.session.commit()

    return success_response(data={
        'id': task.id,
        'name': task.name,
        'is_enabled': task.is_enabled,
    }, message='updated'), 200


@bp.route('/<int:task_id>/history', methods=['GET'])
@jwt_required()
@require_permission('scheduled_task:read')
def get_scheduled_task_history(task_id):
    task = db.session.get(ScheduledTask, task_id)
    if not task:
        return error_response(message='scheduled task not found', code=404), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = TestExecution.query.filter_by(suite_id=task.suite_id).order_by(TestExecution.created_at.desc())
    data = paginate_response(query, page, per_page)
    items = []
    for item in data.pop('items'):
        items.append({
            'id': item.id,
            'suite_id': item.suite_id,
            'environment_id': item.environment_id,
            'status': item.status,
            'total_count': item.total_count,
            'pass_count': item.pass_count,
            'fail_count': item.fail_count,
            'duration': item.duration,
            'started_at': item.started_at.isoformat() if item.started_at else None,
            'finished_at': item.finished_at.isoformat() if item.finished_at else None,
            'created_at': item.created_at.isoformat() if item.created_at else None,
        })

    return success_response(data={**data, 'items': items}), 200
