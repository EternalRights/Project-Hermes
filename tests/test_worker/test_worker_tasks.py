import pytest
from unittest.mock import patch, MagicMock

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'hermes-worker'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'hermes-server'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'hermes-core'))

if 'hermes_core' not in sys.modules:
    import hermes_core as _hc
    sys.modules['hermes_core'] = _hc

if 'hermes_server' not in sys.modules:
    sys.modules['hermes_server'] = MagicMock()
    sys.modules['hermes_server.app'] = MagicMock()
    sys.modules['hermes_server.models'] = MagicMock()
    sys.modules['hermes_server.models.execution'] = MagicMock()
    sys.modules['hermes_server.models.test_case'] = MagicMock()
    sys.modules['hermes_server.models.project'] = MagicMock()
    sys.modules['hermes_server.models.notification'] = MagicMock()
    sys.modules['hermes_server.models.scheduled_task'] = MagicMock()


class TestCeleryConfig:
    def test_config_loads_from_env(self):
        from hermes_worker.config import CeleryConfig
        assert CeleryConfig.broker_url is not None
        assert CeleryConfig.result_backend is not None

    def test_config_serialization(self):
        from hermes_worker.config import CeleryConfig
        config_dict = CeleryConfig.as_dict()
        assert 'broker_url' in config_dict
        assert 'result_backend' in config_dict
        assert config_dict['task_serializer'] == 'json'
        assert config_dict['result_serializer'] == 'json'

    def test_config_defaults(self):
        from hermes_worker.config import CeleryConfig
        assert CeleryConfig.task_track_started is True
        assert CeleryConfig.worker_prefetch_multiplier == 1
        assert CeleryConfig.task_acks_late is True


class TestTaskDefinitions:
    def test_execute_test_case_task_exists(self):
        from hermes_worker.tasks.test_execution import execute_test_case
        assert execute_test_case is not None
        assert execute_test_case.name == 'hermes_worker.tasks.execute_test_case'

    def test_execute_test_suite_task_exists(self):
        from hermes_worker.tasks.test_execution import execute_test_suite
        assert execute_test_suite is not None
        assert execute_test_suite.name == 'hermes_worker.tasks.execute_test_suite'

    def test_execute_scheduled_task_exists(self):
        from hermes_worker.tasks.test_execution import execute_scheduled_task
        assert execute_scheduled_task is not None
        assert execute_scheduled_task.name == 'hermes_worker.tasks.execute_scheduled_task'

    def test_heartbeat_task_exists(self):
        from hermes_worker.tasks.heartbeat import heartbeat
        assert heartbeat is not None
        assert heartbeat.name == 'hermes_worker.tasks.heartbeat'

    def test_execute_test_case_max_retries(self):
        from hermes_worker.tasks.test_execution import execute_test_case
        assert execute_test_case.max_retries == 3

    def test_execute_test_suite_max_retries(self):
        from hermes_worker.tasks.test_execution import execute_test_suite
        assert execute_test_suite.max_retries == 3
