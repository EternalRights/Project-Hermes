from hermes_server.app import db
from hermes_server.models.test_case import TestSuite, TestSuiteCase, TestCase
from hermes_server.services.exceptions import ValidationError, NotFoundError, DuplicateError


class TestSuiteService:
    @staticmethod
    def list_test_suites(page=1, per_page=20, project_id=None):
        query = TestSuite.query

        if project_id is not None:
            query = query.filter(TestSuite.project_id == project_id)

        query = query.order_by(TestSuite.id.desc())
        return query

    @staticmethod
    def create_test_suite(data, user_id):
        name = data.get('name')
        project_id = data.get('project_id')
        if not name or project_id is None:
            raise ValidationError('name and project_id are required')

        suite = TestSuite(
            name=name,
            project_id=project_id,
            description=data.get('description'),
            execution_mode=data.get('execution_mode', 'serial'),
            created_by=user_id,
        )

        db.session.add(suite)
        db.session.commit()
        return suite

    @staticmethod
    def get_test_suite(suite_id):
        suite = db.session.get(TestSuite, suite_id)
        if not suite:
            raise NotFoundError('test suite not found')
        return suite

    @staticmethod
    def get_test_suite_detail(suite_id):
        suite = TestSuiteService.get_test_suite(suite_id)
        suite_cases = suite.suite_cases.order_by(TestSuiteCase.sort_order.asc()).all()
        return suite, [sc.to_dict() for sc in suite_cases]

    @staticmethod
    def update_test_suite(suite_id, data):
        suite = TestSuiteService.get_test_suite(suite_id)

        updatable_fields = ['name', 'description', 'execution_mode']
        for field in updatable_fields:
            if field in data:
                setattr(suite, field, data[field])

        db.session.commit()
        return suite

    @staticmethod
    def delete_test_suite(suite_id):
        suite = TestSuiteService.get_test_suite(suite_id)
        TestSuiteCase.query.filter(TestSuiteCase.suite_id == suite_id).delete()
        db.session.delete(suite)
        db.session.commit()

    @staticmethod
    def add_case_to_suite(suite_id, data):
        suite = TestSuiteService.get_test_suite(suite_id)

        case_id = data.get('case_id')
        if case_id is None:
            raise ValidationError('case_id is required')

        case = db.session.get(TestCase, case_id)
        if not case:
            raise NotFoundError('test case not found')

        existing = TestSuiteCase.query.filter_by(suite_id=suite_id, case_id=case_id).first()
        if existing:
            raise DuplicateError('case already exists in suite')

        suite_case = TestSuiteCase(
            suite_id=suite_id,
            case_id=case_id,
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True),
        )

        db.session.add(suite_case)
        db.session.commit()
        return suite_case

    @staticmethod
    def remove_case_from_suite(suite_id, case_id):
        TestSuiteService.get_test_suite(suite_id)

        suite_case = TestSuiteCase.query.filter_by(suite_id=suite_id, case_id=case_id).first()
        if not suite_case:
            raise NotFoundError('case not found in suite')

        db.session.delete(suite_case)
        db.session.commit()

    @staticmethod
    def reorder_suite_cases(suite_id, orders):
        TestSuiteService.get_test_suite(suite_id)

        if not isinstance(orders, list):
            raise ValidationError('orders must be a list')

        for item in orders:
            case_id = item.get('case_id')
            sort_order = item.get('sort_order')
            if case_id is None or sort_order is None:
                continue

            suite_case = TestSuiteCase.query.filter_by(suite_id=suite_id, case_id=case_id).first()
            if suite_case:
                suite_case.sort_order = sort_order

        db.session.commit()

    @staticmethod
    def toggle_suite_case(suite_id, case_id, is_enabled):
        TestSuiteService.get_test_suite(suite_id)

        suite_case = TestSuiteCase.query.filter_by(suite_id=suite_id, case_id=case_id).first()
        if not suite_case:
            raise NotFoundError('case not found in suite')

        suite_case.is_enabled = is_enabled
        db.session.commit()
        return suite_case
