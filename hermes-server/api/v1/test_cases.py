import copy
import io
import yaml

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_server.app import db
from hermes_server.models.test_case import TestCase
from hermes_server.models.data_source import DataSource
from hermes_server.app.response import success_response, error_response, paginate_response
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

    query = TestCase.query

    if project_id is not None:
        query = query.filter(TestCase.project_id == project_id)
    if module:
        query = query.filter(TestCase.module == module)
    if priority:
        query = query.filter(TestCase.priority == priority)
    if status:
        query = query.filter(TestCase.status == status)

    query = query.order_by(TestCase.id.desc())
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

    name = data.get('name')
    project_id = data.get('project_id')
    if not name or project_id is None:
        return jsonify(error_response(message='name and project_id are required')), 400

    current_user_id = get_jwt_identity()

    case = TestCase(
        name=name,
        project_id=project_id,
        module=data.get('module'),
        tags=data.get('tags'),
        priority=data.get('priority', 'P2'),
        status='draft',
        request_config=data.get('request_config'),
        assertions=data.get('assertions'),
        pre_hooks=data.get('pre_hooks'),
        post_hooks=data.get('post_hooks'),
        variables=data.get('variables'),
        data_source_id=data.get('data_source_id'),
        retry_config=data.get('retry_config'),
        timeout=data.get('timeout', 30000),
        created_by=current_user_id,
    )

    db.session.add(case)
    db.session.commit()

    return jsonify(success_response(data=case.to_dict(), code=201)), 201


@bp.route('/<int:case_id>', methods=['GET'])
@jwt_required()
@require_permission('test_case:read')
def get_test_case(case_id):
    case = TestCase.query.get(case_id)
    if not case:
        return jsonify(error_response(message='test case not found', code=404)), 404
    return jsonify(success_response(data=case.to_dict()))


@bp.route('/<int:case_id>', methods=['PUT'])
@jwt_required()
@require_permission('test_case:update')
def update_test_case(case_id):
    case = TestCase.query.get(case_id)
    if not case:
        return jsonify(error_response(message='test case not found', code=404)), 404

    data = request.get_json()
    if not data:
        return jsonify(error_response(message='request body is required')), 400

    updatable_fields = [
        'name', 'module', 'tags', 'priority', 'status',
        'request_config', 'assertions', 'pre_hooks', 'post_hooks',
        'variables', 'data_source_id', 'retry_config', 'timeout',
    ]

    for field in updatable_fields:
        if field in data:
            setattr(case, field, data[field])

    db.session.commit()
    return jsonify(success_response(data=case.to_dict()))


@bp.route('/<int:case_id>', methods=['DELETE'])
@jwt_required()
def delete_test_case(case_id):
    case = TestCase.query.get(case_id)
    if not case:
        return jsonify(error_response(message='test case not found', code=404)), 404

    db.session.delete(case)
    db.session.commit()
    return jsonify(success_response(message='deleted'))


@bp.route('/modules', methods=['GET'])
@jwt_required()
def get_modules():
    project_id = request.args.get('project_id', type=int)
    if project_id is None:
        return jsonify(error_response(message='project_id is required')), 400

    modules = db.session.query(TestCase.module).filter(
        TestCase.project_id == project_id,
        TestCase.module.isnot(None),
    ).distinct().all()

    module_list = [m[0] for m in modules if m[0]]
    return jsonify(success_response(data=module_list))


@bp.route('/tags', methods=['GET'])
@jwt_required()
def get_tags():
    project_id = request.args.get('project_id', type=int)
    if project_id is None:
        return jsonify(error_response(message='project_id is required')), 400

    cases = TestCase.query.filter(
        TestCase.project_id == project_id,
        TestCase.tags.isnot(None),
    ).all()

    tag_set = set()
    for case in cases:
        if isinstance(case.tags, list):
            for tag in case.tags:
                tag_set.add(tag)

    return jsonify(success_response(data=sorted(list(tag_set))))


@bp.route('/<int:case_id>/tags', methods=['PUT'])
@jwt_required()
def update_test_case_tags(case_id):
    case = TestCase.query.get(case_id)
    if not case:
        return jsonify(error_response(message='test case not found', code=404)), 404

    data = request.get_json()
    if not data or 'tags' not in data:
        return jsonify(error_response(message='tags is required')), 400

    case.tags = data['tags']
    db.session.commit()
    return jsonify(success_response(data=case.to_dict()))


@bp.route('/<int:case_id>/copy', methods=['POST'])
@jwt_required()
def copy_test_case(case_id):
    case = TestCase.query.get(case_id)
    if not case:
        return jsonify(error_response(message='test case not found', code=404)), 404

    current_user_id = get_jwt_identity()

    new_case = TestCase(
        name=f'{case.name}_副本',
        project_id=case.project_id,
        module=case.module,
        tags=copy.deepcopy(case.tags) if case.tags else None,
        priority=case.priority,
        status='draft',
        request_config=copy.deepcopy(case.request_config) if case.request_config else None,
        assertions=copy.deepcopy(case.assertions) if case.assertions else None,
        pre_hooks=copy.deepcopy(case.pre_hooks) if case.pre_hooks else None,
        post_hooks=copy.deepcopy(case.post_hooks) if case.post_hooks else None,
        variables=copy.deepcopy(case.variables) if case.variables else None,
        data_source_id=case.data_source_id,
        retry_config=copy.deepcopy(case.retry_config) if case.retry_config else None,
        timeout=case.timeout,
        created_by=current_user_id,
    )

    db.session.add(new_case)
    db.session.commit()

    return jsonify(success_response(data=new_case.to_dict(), code=201)), 201


@bp.route('/export', methods=['GET'])
@jwt_required()
def export_test_cases():
    project_id = request.args.get('project_id', type=int)
    ids_param = request.args.get('ids', type=str)
    export_format = request.args.get('format', 'json', type=str)

    if project_id is None:
        return jsonify(error_response(message='project_id is required')), 400

    query = TestCase.query.filter(TestCase.project_id == project_id)

    if ids_param:
        try:
            ids = [int(i.strip()) for i in ids_param.split(',') if i.strip()]
            query = query.filter(TestCase.id.in_(ids))
        except ValueError:
            return jsonify(error_response(message='invalid ids format')), 400

    cases = query.order_by(TestCase.id.asc()).all()
    export_data = [case.to_dict() for case in cases]

    if export_format == 'yaml':
        yaml_content = yaml.dump(export_data, allow_unicode=True, default_flow_style=False)
        return jsonify(success_response(data=yaml_content))
    else:
        return jsonify(success_response(data=export_data))


@bp.route('/import', methods=['POST'])
@jwt_required()
def import_test_cases():
    data = request.get_json()
    if not data:
        return jsonify(error_response(message='request body is required')), 400

    project_id = data.get('project_id')
    cases = data.get('cases')

    if project_id is None or not isinstance(cases, list):
        return jsonify(error_response(message='project_id and cases are required')), 400

    current_user_id = get_jwt_identity()
    imported = []

    for case_data in cases:
        case = TestCase(
            name=case_data.get('name', 'unnamed'),
            project_id=project_id,
            module=case_data.get('module'),
            tags=case_data.get('tags'),
            priority=case_data.get('priority', 'P2'),
            status='draft',
            request_config=case_data.get('request_config'),
            assertions=case_data.get('assertions'),
            pre_hooks=case_data.get('pre_hooks'),
            post_hooks=case_data.get('post_hooks'),
            variables=case_data.get('variables'),
            data_source_id=case_data.get('data_source_id'),
            retry_config=case_data.get('retry_config'),
            timeout=case_data.get('timeout', 30000),
            created_by=current_user_id,
        )
        db.session.add(case)
        imported.append(case)

    db.session.commit()

    result = [case.to_dict() for case in imported]
    return jsonify(success_response(data=result, code=201)), 201
