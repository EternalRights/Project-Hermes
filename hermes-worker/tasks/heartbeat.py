import json
import socket
import logging
from datetime import datetime

import redis

from hermes_worker.celery_app import celery_app
from hermes_worker.config import broker_url

logger = logging.getLogger(__name__)


def _get_redis_client():
    parsed = broker_url
    return redis.from_url(parsed)


@celery_app.task(name='hermes_worker.tasks.heartbeat', bind=True)
def heartbeat(self):
    worker_name = socket.gethostname()
    worker_id = self.request.id or 'unknown'

    status = {
        'worker_name': worker_name,
        'worker_id': worker_id,
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat(),
    }

    try:
        client = _get_redis_client()
        key = f'hermes:worker:heartbeat:{worker_name}'
        client.setex(key, 60, json.dumps(status))
    except Exception as e:
        logger.error('Heartbeat failed: %s', str(e))
