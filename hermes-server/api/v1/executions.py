from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_worker.celery_app import celery_app
from hermes_server.app import db
from hermes_server.models.execution import TestExecution, TestStepResult
from hermes_server.models.test_case import TestSuite, TestSuiteCase
from hermes_server.app.response import success_response, error_response, paginate_response

bp = Blueprint('executions', __name__, url_prefix='/api/v1/executions')


@bp.route('', methods=['POST'])
@jwt_required()
def create_execution():
    data = request.get_json()
    if not data:
        return jsonify(error_response(message='request body is required')), 400

    suite_id = data.get('suite_id')
    environment_id = data.get('environment_id')
    if suite_id is None or environment_id is None:
        return jsonify(error_response(message='suite_id and environment_id are required')), 400

    suite = TestSuite.query.get(suite_id)
    if not suite:
        return jsonify(error_response(message='test suite not found', code=404)), 404

    current_user_id = get_jwt_identity()

    execution = TestExecution(
        suite_id=suite_id,
        environment_id=environment_id,
        plan_id=data.get('plan_id'),
        status='pending',
        created_by=current_user_id,
    )

    db.session.add(execution)
    db.session.commit()

    celery_app.send_task(
        'hermes_worker.tasks.execute_test_suite',
        args=[execution.id, execution.suite_id, execution.environment_id],
    )

    return jsonify(success_response(data={
        'id': execution.id,
        'suite_id': execution.suite_id,
        'environment_id': execution.environment_id,
        'plan_id': execution.plan_id,
        'status': execution.status,
        'created_by': execution.created_by,
        'created_at': execution.created_at.isoformat() if execution.created_at else None,
    }, code=201)), 201


@bp.route('/<int:execution_id>', methods=['GET'])
@jwt_required()
def get_execution(execution_id):
    execution = TestExecution.query.get(execution_id)
    if not execution:
        return jsonify(error_response(message='execution not found', code=404)), 404

    step_results = execution.step_results.order_by(TestStepResult.id.asc()).all()
    step_list = []
    for step in step_results:
        step_list.append({
            'id': step.id,
            'execution_id': step.execution_id,
            'case_id': step.case_id,
            'case_name': step.case_name,
            'status': step.status,
            'request_config': step.request_config,
            'response_status_code': step.response_status_code,
            'response_headers': step.response_headers,
            'response_body': step.response_body,
            'response_time': step.response_time,
            'assertions_result': step.assertions_result,
            'error_message': step.error_message,
            'started_at': step.started_at.isoformat() if step.started_at else None,
            'finished_at': step.finished_at.isoformat() if step.finished_at else None,
        })

    return jsonify(success_response(data={
        'id': execution.id,
        'plan_id': execution.plan_id,
        'suite_id': execution.suite_id,
        'environment_id': execution.environment_id,
        'status': execution.status,
        'total_count': execution.total_count,
        'pass_count': execution.pass_count,
        'fail_count': execution.fail_count,
        'error_count': execution.error_count,
        'skip_count': execution.skip_count,
        'duration': execution.duration,
        'started_at': execution.started_at.isoformat() if execution.started_at else None,
        'finished_at': execution.finished_at.isoformat() if execution.finished_at else None,
        'created_by': execution.created_by,
        'created_at': execution.created_at.isoformat() if execution.created_at else None,
        'step_results': step_list,
    }))


@bp.route('', methods=['GET'])
@jwt_required()
def get_executions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    suite_id = request.args.get('suite_id', type=int)
    status = request.args.get('status', type=str)

    query = TestExecution.query

    if suite_id is not None:
        query = query.filter(TestExecution.suite_id == suite_id)
    if status:
        query = query.filter(TestExecution.status == status)

    query = query.order_by(TestExecution.id.desc())
    result = paginate_response(query, page, per_page)
    items = []
    for execution in result['items']:
        items.append({
            'id': execution.id,
            'plan_id': execution.plan_id,
            'suite_id': execution.suite_id,
            'environment_id': execution.environment_id,
            'status': execution.status,
            'total_count': execution.total_count,
            'pass_count': execution.pass_count,
            'fail_count': execution.fail_count,
            'error_count': execution.error_count,
            'skip_count': execution.skip_count,
            'duration': execution.duration,
            'started_at': execution.started_at.isoformat() if execution.started_at else None,
            'finished_at': execution.finished_at.isoformat() if execution.finished_at else None,
            'created_by': execution.created_by,
            'created_at': execution.created_at.isoformat() if execution.created_at else None,
        })
    result['items'] = items
    return jsonify(success_response(data=result))
