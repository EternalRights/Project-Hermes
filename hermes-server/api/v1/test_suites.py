from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_server.services.test_suite_service import TestSuiteService
from hermes_server.app.response import success_response, error_response, paginate_response
from hermes_server.app.error_handlers import HermesBusinessError
from hermes_server.middleware.permission import require_permission

bp = Blueprint('test_suites', __name__, url_prefix='/api/v1/test-suites')


@bp.route('', methods=['GET'])
@jwt_required()
@require_permission('test_suite:read')
def get_test_suites():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    project_id = request.args.get('project_id', type=int)

    query = TestSuiteService.list_test_suites(page=page, per_page=per_page, project_id=project_id)
    result = paginate_response(query, page, per_page)
    items = [suite.to_dict() for suite in result['items']]
    result['items'] = items
    return jsonify(success_response(data=result))


@bp.route('', methods=['POST'])
@jwt_required()
@require_permission('test_suite:create')
def create_test_suite():
    data = request.get_json()
    if not data:
        return jsonify(error_response(message='request body is required')), 400

    current_user_id = get_jwt_identity()
    try:
        suite = TestSuiteService.create_test_suite(data, current_user_id)
        return jsonify(success_response(data=suite.to_dict(), code=201)), 201
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:suite_id>', methods=['GET'])
@jwt_required()
@require_permission('test_suite:read')
def get_test_suite(suite_id):
    try:
        suite, cases = TestSuiteService.get_test_suite_detail(suite_id)
        data = suite.to_dict()
        data['cases'] = cases
        return jsonify(success_response(data=data))
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:suite_id>', methods=['PUT'])
@jwt_required()
@require_permission('test_suite:update')
def update_test_suite(suite_id):
    data = request.get_json()
    if not data:
        return jsonify(error_response(message='request body is required')), 400

    try:
        suite = TestSuiteService.update_test_suite(suite_id, data)
        return jsonify(success_response(data=suite.to_dict()))
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:suite_id>', methods=['DELETE'])
@jwt_required()
@require_permission('test_suite:delete')
def delete_test_suite(suite_id):
    try:
        TestSuiteService.delete_test_suite(suite_id)
        return jsonify(success_response(message='deleted'))
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:suite_id>/cases', methods=['POST'])
@jwt_required()
def add_case_to_suite(suite_id):
    data = request.get_json()
    if not data:
        return jsonify(error_response(message='request body is required')), 400

    try:
        suite_case = TestSuiteService.add_case_to_suite(suite_id, data)
        return jsonify(success_response(data=suite_case.to_dict(), code=201)), 201
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:suite_id>/cases/<int:case_id>', methods=['DELETE'])
@jwt_required()
def remove_case_from_suite(suite_id, case_id):
    try:
        TestSuiteService.remove_case_from_suite(suite_id, case_id)
        return jsonify(success_response(message='removed'))
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:suite_id>/cases/reorder', methods=['PUT'])
@jwt_required()
def reorder_suite_cases(suite_id):
    data = request.get_json()
    if not data or 'orders' not in data:
        return jsonify(error_response(message='orders is required')), 400

    try:
        TestSuiteService.reorder_suite_cases(suite_id, data.get('orders'))
        return jsonify(success_response(message='reordered'))
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:suite_id>/cases/<int:case_id>/toggle', methods=['PUT'])
@jwt_required()
def toggle_suite_case(suite_id, case_id):
    data = request.get_json()
    if not data or 'is_enabled' not in data:
        return jsonify(error_response(message='is_enabled is required')), 400

    try:
        suite_case = TestSuiteService.toggle_suite_case(suite_id, case_id, data['is_enabled'])
        return jsonify(success_response(data=suite_case.to_dict()))
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code
