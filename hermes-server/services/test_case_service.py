import copy

import yaml

from hermes_server.app import db
from hermes_server.models.test_case import TestCase
from hermes_server.services.exceptions import ValidationError, NotFoundError


class TestCaseService:
    @staticmethod
    def list_test_cases(page=1, per_page=20, project_id=None, module=None, priority=None, status=None):
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
        return query

    @staticmethod
    def create_test_case(data, user_id):
        name = data.get('name')
        project_id = data.get('project_id')
        if not name or project_id is None:
            raise ValidationError('name and project_id are required')

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
            created_by=user_id,
        )

        db.session.add(case)
        db.session.commit()
        return case

    @staticmethod
    def get_test_case(case_id):
        case = db.session.get(TestCase, case_id)
        if not case:
            raise NotFoundError('test case not found')
        return case

    @staticmethod
    def update_test_case(case_id, data):
        case = TestCaseService.get_test_case(case_id)

        updatable_fields = [
            'name', 'module', 'tags', 'priority', 'status',
            'request_config', 'assertions', 'pre_hooks', 'post_hooks',
            'variables', 'data_source_id', 'retry_config', 'timeout',
        ]

        for field in updatable_fields:
            if field in data:
                setattr(case, field, data[field])

        db.session.commit()
        return case

    @staticmethod
    def delete_test_case(case_id):
        case = TestCaseService.get_test_case(case_id)
        db.session.delete(case)
        db.session.commit()

    @staticmethod
    def get_modules(project_id):
        if project_id is None:
            raise ValidationError('project_id is required')

        modules = db.session.query(TestCase.module).filter(
            TestCase.project_id == project_id,
            TestCase.module.isnot(None),
        ).distinct().all()

        return [m[0] for m in modules if m[0]]

    @staticmethod
    def get_tags(project_id):
        if project_id is None:
            raise ValidationError('project_id is required')

        cases = TestCase.query.filter(
            TestCase.project_id == project_id,
            TestCase.tags.isnot(None),
        ).all()

        tag_set = set()
        for case in cases:
            if isinstance(case.tags, list):
                for tag in case.tags:
                    tag_set.add(tag)

        return sorted(list(tag_set))

    @staticmethod
    def update_tags(case_id, tags):
        case = TestCaseService.get_test_case(case_id)
        case.tags = tags
        db.session.commit()
        return case

    @staticmethod
    def copy_test_case(case_id, user_id):
        case = TestCaseService.get_test_case(case_id)

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
            created_by=user_id,
        )

        db.session.add(new_case)
        db.session.commit()
        return new_case

    @staticmethod
    def export_test_cases(project_id, ids=None, export_format='json'):
        if project_id is None:
            raise ValidationError('project_id is required')

        query = TestCase.query.filter(TestCase.project_id == project_id)

        if ids:
            query = query.filter(TestCase.id.in_(ids))

        cases = query.order_by(TestCase.id.asc()).all()
        export_data = [case.to_dict() for case in cases]

        if export_format == 'yaml':
            return yaml.dump(export_data, allow_unicode=True, default_flow_style=False)
        return export_data

    @staticmethod
    def import_test_cases(project_id, cases_data, user_id):
        if project_id is None or not isinstance(cases_data, list):
            raise ValidationError('project_id and cases are required')

        imported = []
        for case_data in cases_data:
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
                created_by=user_id,
            )
            db.session.add(case)
            imported.append(case)

        db.session.commit()
        return imported
