from hermes_server.app import db
from hermes_server.models.execution import TestExecution
from hermes_server.models.test_case import TestSuite
from hermes_server.services.exceptions import ValidationError, NotFoundError


class ExecutionService:
    @staticmethod
    def create_execution(data, user_id):
        suite_id = data.get('suite_id')
        environment_id = data.get('environment_id')
        if suite_id is None or environment_id is None:
            raise ValidationError('suite_id and environment_id are required')

        suite = db.session.get(TestSuite, suite_id)
        if not suite:
            raise NotFoundError('test suite not found')

        execution = TestExecution(
            suite_id=suite_id,
            environment_id=environment_id,
            plan_id=data.get('plan_id'),
            status='pending',
            created_by=user_id,
        )

        db.session.add(execution)
        db.session.commit()
        return execution

    @staticmethod
    def get_execution(execution_id):
        execution = db.session.get(TestExecution, execution_id)
        if not execution:
            raise NotFoundError('execution not found')
        return execution

    @staticmethod
    def get_execution_detail(execution_id):
        execution = ExecutionService.get_execution(execution_id)
        return execution.to_dict(include_steps=True)

    @staticmethod
    def list_executions(page=1, per_page=20, suite_id=None, status=None):
        query = TestExecution.query

        if suite_id is not None:
            query = query.filter(TestExecution.suite_id == suite_id)
        if status:
            query = query.filter(TestExecution.status == status)

        query = query.order_by(TestExecution.id.desc())
        return query
