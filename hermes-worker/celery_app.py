import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'hermes-server'))

from celery import Celery
from celery.schedules import crontab

celery_app = Celery('hermes_worker')

celery_app.config_from_object('hermes_worker.config')

celery_app.autodiscover_tasks(['hermes_worker.tasks'])

beat_schedule = {
    'check-scheduled-tasks': {
        'task': 'hermes_worker.tasks.check_scheduled_tasks',
        'schedule': 60.0,
    },
}
celery_app.conf.beat_schedule = beat_schedule
