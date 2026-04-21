from datetime import datetime, timezone

from hermes_core.scheduler.cron_parser import CronParser


class Scheduler:
    def __init__(self, app):
        self.app = app

    def check_and_update_scheduled_tasks(self):
        from hermes_server.app import db
        from hermes_server.models.scheduled_task import ScheduledTask

        with self.app.app_context():
            tasks = ScheduledTask.query.filter_by(is_enabled=True).all()
            now = datetime.now(timezone.utc)
            for task in tasks:
                try:
                    next_time = CronParser.next_run_time(task.cron_expression, after=now)
                    task.next_run_at = next_time
                except ValueError:
                    continue
            db.session.commit()
