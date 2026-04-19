import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'hermes-server'))

from celery import Celery

celery_app = Celery('hermes_worker')

celery_app.config_from_object('hermes_worker.config')

celery_app.autodiscover_tasks(['hermes_worker.tasks'])
