from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_server.services.test_case_service import TestCaseService
from hermes_server.app.response import success_response, error_response, paginate_response
from hermes_server.app.error_handlers import HermesBusinessError
from hermes_server.middleware.permission import require_permission

bp = Blueprint('test_cases', __name__, url_prefix='/api/v1/test-cases')


@bp.route('', methods=['GET'])
@jwt_required()
@require_permission('test_case:read')
def get_test_cases():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    project_id = request.args.get('project_id', type=int)
    module = request.args.get('module', type=str)
    priority = request.args.get('priority', type=str)
    status = request.args.get('status', type=str)

    query = TestCaseService.list_test_cases(
        page=page, per_page=per_page,
        project_id=project_id, module=module, priority=priority, status=status,
    )
    result = paginate_response(query, page, per_page)
    items = [case.to_dict() for case in result['items']]
    result['items'] = items
    return jsonify(success_response(data=result))


@bp.route('', methods=['POST'])
@jwt_required()
@require_permission('test_case:create')
def create_test_case():
    data = request.get_json()
    if not data:
        return jsonify(error_response(message='request body is required')), 400

    current_user_id = get_jwt_identity()
    try:
        case = TestCaseService.create_test_case(data, current_user_id)
        return jsonify(success_response(data=case.to_dict(), code=201)), 201
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:case_id>', methods=['GET'])
@jwt_required()
@require_permission('test_case:read')
def get_test_case(case_id):
    try:
        case = TestCaseService.get_test_case(case_id)
        return jsonify(success_response(data=case.to_dict()))
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:case_id>', methods=['PUT'])
@jwt_required()
@require_permission('test_case:update')
def update_test_case(case_id):
    data = request.get_json()
    if not data:
        return jsonify(error_response(message='request body is required')), 400

    try:
        case = TestCaseService.update_test_case(case_id, data)
        return jsonify(success_response(data=case.to_dict()))
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:case_id>', methods=['DELETE'])
@jwt_required()
@require_permission('test_case:delete')
def delete_test_case(case_id):
    try:
        TestCaseService.delete_test_case(case_id)
        return jsonify(success_response(message='deleted'))
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/modules', methods=['GET'])
@jwt_required()
def get_modules():
    project_id = request.args.get('project_id', type=int)
    try:
        modules = TestCaseService.get_modules(project_id)
        return jsonify(success_response(data=modules))
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/tags', methods=['GET'])
@jwt_required()
def get_tags():
    project_id = request.args.get('project_id', type=int)
    try:
        tags = TestCaseService.get_tags(project_id)
        return jsonify(success_response(data=tags))
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:case_id>/tags', methods=['PUT'])
@jwt_required()
def update_test_case_tags(case_id):
    data = request.get_json()
    if not data or 'tags' not in data:
        return jsonify(error_response(message='tags is required')), 400

    try:
        case = TestCaseService.update_tags(case_id, data['tags'])
        return jsonify(success_response(data=case.to_dict()))
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:case_id>/copy', methods=['POST'])
@jwt_required()
def copy_test_case(case_id):
    current_user_id = get_jwt_identity()
    try:
        new_case = TestCaseService.copy_test_case(case_id, current_user_id)
        return jsonify(success_response(data=new_case.to_dict(), code=201)), 201
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/export', methods=['GET'])
@jwt_required()
def export_test_cases():
    project_id = request.args.get('project_id', type=int)
    ids_param = request.args.get('ids', type=str)
    export_format = request.args.get('format', 'json', type=str)

    ids = None
    if ids_param:
        try:
            ids = [int(i.strip()) for i in ids_param.split(',') if i.strip()]
        except ValueError:
            return jsonify(error_response(message='invalid ids format')), 400

    try:
        data = TestCaseService.export_test_cases(project_id, ids=ids, export_format=export_format)
        return jsonify(success_response(data=data))
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/import', methods=['POST'])
@jwt_required()
def import_test_cases():
    data = request.get_json()
    if not data:
        return jsonify(error_response(message='request body is required')), 400

    project_id = data.get('project_id')
    cases = data.get('cases')
    current_user_id = get_jwt_identity()

    try:
        imported = TestCaseService.import_test_cases(project_id, cases, current_user_id)
        result = [case.to_dict() for case in imported]
        return jsonify(success_response(data=result, code=201)), 201
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code
