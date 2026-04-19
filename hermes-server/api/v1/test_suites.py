from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_server.app import db
from hermes_server.models.test_case import TestSuite, TestSuiteCase, TestCase
from hermes_server.app.response import success_response, error_response, paginate_response

bp = Blueprint('test_suites', __name__, url_prefix='/api/v1/test-suites')


@bp.route('', methods=['GET'])
@jwt_required()
def get_test_suites():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    project_id = request.args.get('project_id', type=int)

    query = TestSuite.query

    if project_id is not None:
        query = query.filter(TestSuite.project_id == project_id)

    query = query.order_by(TestSuite.id.desc())
    result = paginate_response(query, page, per_page)
    items = []
    for suite in result['items']:
        items.append({
            'id': suite.id,
            'name': suite.name,
            'project_id': suite.project_id,
            'description': suite.description,
            'execution_mode': suite.execution_mode,
            'created_by': suite.created_by,
            'created_at': suite.created_at.isoformat() if suite.created_at else None,
            'updated_at': suite.updated_at.isoformat() if suite.updated_at else None,
        })
    result['items'] = items
    return jsonify(success_response(data=result))


@bp.route('', methods=['POST'])
@jwt_required()
def create_test_suite():
    data = request.get_json()
    if not data:
        return jsonify(error_response(message='request body is required')), 400

    name = data.get('name')
    project_id = data.get('project_id')
    if not name or project_id is None:
        return jsonify(error_response(message='name and project_id are required')), 400

    current_user_id = get_jwt_identity()

    suite = TestSuite(
        name=name,
        project_id=project_id,
        description=data.get('description'),
        execution_mode=data.get('execution_mode', 'serial'),
        created_by=current_user_id,
    )

    db.session.add(suite)
    db.session.commit()

    return jsonify(success_response(data={
        'id': suite.id,
        'name': suite.name,
        'project_id': suite.project_id,
        'description': suite.description,
        'execution_mode': suite.execution_mode,
        'created_by': suite.created_by,
        'created_at': suite.created_at.isoformat() if suite.created_at else None,
        'updated_at': suite.updated_at.isoformat() if suite.updated_at else None,
    }, code=201)), 201


@bp.route('/<int:suite_id>', methods=['GET'])
@jwt_required()
def get_test_suite(suite_id):
    suite = TestSuite.query.get(suite_id)
    if not suite:
        return jsonify(error_response(message='test suite not found', code=404)), 404

    suite_cases = suite.suite_cases.order_by(TestSuiteCase.sort_order.asc()).all()
    case_list = []
    for sc in suite_cases:
        case = sc.test_case
        case_list.append({
            'id': sc.id,
            'suite_id': sc.suite_id,
            'case_id': sc.case_id,
            'sort_order': sc.sort_order,
            'is_enabled': sc.is_enabled,
            'test_case': case.to_dict() if case else None,
        })

    return jsonify(success_response(data={
        'id': suite.id,
        'name': suite.name,
        'project_id': suite.project_id,
        'description': suite.description,
        'execution_mode': suite.execution_mode,
        'created_by': suite.created_by,
        'created_at': suite.created_at.isoformat() if suite.created_at else None,
        'updated_at': suite.updated_at.isoformat() if suite.updated_at else None,
        'cases': case_list,
    }))


@bp.route('/<int:suite_id>', methods=['PUT'])
@jwt_required()
def update_test_suite(suite_id):
    suite = TestSuite.query.get(suite_id)
    if not suite:
        return jsonify(error_response(message='test suite not found', code=404)), 404

    data = request.get_json()
    if not data:
        return jsonify(error_response(message='request body is required')), 400

    updatable_fields = ['name', 'description', 'execution_mode']

    for field in updatable_fields:
        if field in data:
            setattr(suite, field, data[field])

    db.session.commit()

    return jsonify(success_response(data={
        'id': suite.id,
        'name': suite.name,
        'project_id': suite.project_id,
        'description': suite.description,
        'execution_mode': suite.execution_mode,
        'created_by': suite.created_by,
        'created_at': suite.created_at.isoformat() if suite.created_at else None,
        'updated_at': suite.updated_at.isoformat() if suite.updated_at else None,
    }))


@bp.route('/<int:suite_id>', methods=['DELETE'])
@jwt_required()
def delete_test_suite(suite_id):
    suite = TestSuite.query.get(suite_id)
    if not suite:
        return jsonify(error_response(message='test suite not found', code=404)), 404

    TestSuiteCase.query.filter(TestSuiteCase.suite_id == suite_id).delete()
    db.session.delete(suite)
    db.session.commit()
    return jsonify(success_response(message='deleted'))


@bp.route('/<int:suite_id>/cases', methods=['POST'])
@jwt_required()
def add_case_to_suite(suite_id):
    suite = TestSuite.query.get(suite_id)
    if not suite:
        return jsonify(error_response(message='test suite not found', code=404)), 404

    data = request.get_json()
    if not data:
        return jsonify(error_response(message='request body is required')), 400

    case_id = data.get('case_id')
    if case_id is None:
        return jsonify(error_response(message='case_id is required')), 400

    case = TestCase.query.get(case_id)
    if not case:
        return jsonify(error_response(message='test case not found', code=404)), 404

    existing = TestSuiteCase.query.filter_by(suite_id=suite_id, case_id=case_id).first()
    if existing:
        return jsonify(error_response(message='case already exists in suite')), 400

    suite_case = TestSuiteCase(
        suite_id=suite_id,
        case_id=case_id,
        sort_order=data.get('sort_order', 0),
        is_enabled=data.get('is_enabled', True),
    )

    db.session.add(suite_case)
    db.session.commit()

    return jsonify(success_response(data={
        'id': suite_case.id,
        'suite_id': suite_case.suite_id,
        'case_id': suite_case.case_id,
        'sort_order': suite_case.sort_order,
        'is_enabled': suite_case.is_enabled,
    }, code=201)), 201


@bp.route('/<int:suite_id>/cases/<int:case_id>', methods=['DELETE'])
@jwt_required()
def remove_case_from_suite(suite_id, case_id):
    suite = TestSuite.query.get(suite_id)
    if not suite:
        return jsonify(error_response(message='test suite not found', code=404)), 404

    suite_case = TestSuiteCase.query.filter_by(suite_id=suite_id, case_id=case_id).first()
    if not suite_case:
        return jsonify(error_response(message='case not found in suite', code=404)), 404

    db.session.delete(suite_case)
    db.session.commit()
    return jsonify(success_response(message='removed'))


@bp.route('/<int:suite_id>/cases/reorder', methods=['PUT'])
@jwt_required()
def reorder_suite_cases(suite_id):
    suite = TestSuite.query.get(suite_id)
    if not suite:
        return jsonify(error_response(message='test suite not found', code=404)), 404

    data = request.get_json()
    if not data or 'orders' not in data:
        return jsonify(error_response(message='orders is required')), 400

    orders = data.get('orders')
    if not isinstance(orders, list):
        return jsonify(error_response(message='orders must be a list')), 400

    for item in orders:
        case_id = item.get('case_id')
        sort_order = item.get('sort_order')
        if case_id is None or sort_order is None:
            continue

        suite_case = TestSuiteCase.query.filter_by(suite_id=suite_id, case_id=case_id).first()
        if suite_case:
            suite_case.sort_order = sort_order

    db.session.commit()
    return jsonify(success_response(message='reordered'))


@bp.route('/<int:suite_id>/cases/<int:case_id>/toggle', methods=['PUT'])
@jwt_required()
def toggle_suite_case(suite_id, case_id):
    suite = TestSuite.query.get(suite_id)
    if not suite:
        return jsonify(error_response(message='test suite not found', code=404)), 404

    suite_case = TestSuiteCase.query.filter_by(suite_id=suite_id, case_id=case_id).first()
    if not suite_case:
        return jsonify(error_response(message='case not found in suite', code=404)), 404

    data = request.get_json()
    if not data or 'is_enabled' not in data:
        return jsonify(error_response(message='is_enabled is required')), 400

    suite_case.is_enabled = data['is_enabled']
    db.session.commit()

    return jsonify(success_response(data={
        'id': suite_case.id,
        'suite_id': suite_case.suite_id,
        'case_id': suite_case.case_id,
        'sort_order': suite_case.sort_order,
        'is_enabled': suite_case.is_enabled,
    }))
