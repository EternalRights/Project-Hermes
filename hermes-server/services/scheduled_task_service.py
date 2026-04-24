from hermes_server.app import db
from hermes_server.models.scheduled_task import ScheduledTask
from hermes_server.models.execution import TestExecution
from hermes_server.services.exceptions import ValidationError, NotFoundError


class ScheduledTaskService:
    @staticmethod
    def list_scheduled_tasks(page=1, per_page=10, project_id=None):
        query = ScheduledTask.query
        if project_id:
            query = query.filter_by(project_id=project_id)
        query = query.order_by(ScheduledTask.created_at.desc())
        return query

    @staticmethod
    def create_scheduled_task(data, user_id):
        name = data.get('name')
        project_id = data.get('project_id')
        suite_id = data.get('suite_id')
        environment_id = data.get('environment_id')
        cron_expression = data.get('cron_expression')

        if not all([name, project_id, suite_id, environment_id, cron_expression]):
            raise ValidationError('name, project_id, suite_id, environment_id, cron_expression are required')

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
        return task

    @staticmethod
    def get_scheduled_task(task_id):
        task = db.session.get(ScheduledTask, task_id)
        if not task:
            raise NotFoundError('scheduled task not found')
        return task

    @staticmethod
    def update_scheduled_task(task_id, data):
        task = ScheduledTaskService.get_scheduled_task(task_id)

        updatable_fields = ['name', 'project_id', 'suite_id', 'environment_id', 'cron_expression']
        for field in updatable_fields:
            if field in data:
                setattr(task, field, data[field])

        db.session.commit()
        return task

    @staticmethod
    def delete_scheduled_task(task_id):
        task = ScheduledTaskService.get_scheduled_task(task_id)
        db.session.delete(task)
        db.session.commit()

    @staticmethod
    def toggle_scheduled_task(task_id, is_enabled):
        task = ScheduledTaskService.get_scheduled_task(task_id)
        task.is_enabled = is_enabled
        db.session.commit()
        return task

    @staticmethod
    def get_task_history(task_id, page=1, per_page=10):
        task = ScheduledTaskService.get_scheduled_task(task_id)
        query = TestExecution.query.filter_by(suite_id=task.suite_id).order_by(TestExecution.created_at.desc())
        return query
