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

sys.modules['redis'] = MagicMock()


class TestWorkerConfig:
    def test_config_module_loads(self):
        from hermes_worker import config
        assert hasattr(config, 'broker_url')
        assert hasattr(config, 'result_backend')

    def test_config_values(self):
        from hermes_worker.config import broker_url, result_backend
        assert broker_url is not None
        assert result_backend is not None


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


class TestExecuteTestCaseLogic:
    @patch('hermes_worker.tasks.test_execution._get_app')
    def test_execute_test_case_valid(self, mock_get_app):
        mock_app = MagicMock()
        mock_get_app.return_value = mock_app

        mock_case = MagicMock()
        mock_case.id = 1
        mock_case.name = "Test Case 1"
        mock_case.created_by = 1
        mock_case.variables = {}
        mock_case.request_config = {"method": "GET", "url": "http://localhost/test"}
        mock_case.assertions = []
        mock_case.pre_hooks = []
        mock_case.post_hooks = []

        mock_env = MagicMock()
        mock_env.id = 1
        mock_env.variables = {}
        mock_env.base_url = "http://localhost"

        mock_session = MagicMock()
        mock_session.get.side_effect = [mock_case, mock_env]

        mock_db = MagicMock()
        mock_db.session = mock_session

        with patch.dict('sys.modules', {
            'hermes_server.app': MagicMock(db=mock_db),
            'hermes_server.models.execution': MagicMock(TestExecution=MagicMock(), TestStepResult=MagicMock()),
            'hermes_server.models.test_case': MagicMock(TestCase=MagicMock()),
            'hermes_server.models.project': MagicMock(Environment=MagicMock(), GlobalVariable=MagicMock()),
        }):
            from hermes_worker.tasks.test_execution import execute_test_case
            result = execute_test_case(case_id=1, environment_id=1)
            assert result is not None or mock_session.add.called or mock_session.commit.called

    @patch('hermes_worker.tasks.test_execution._get_app')
    def test_execute_test_case_nonexistent_case(self, mock_get_app):
        mock_app = MagicMock()
        mock_get_app.return_value = mock_app

        mock_session = MagicMock()
        mock_session.get.return_value = None

        mock_db = MagicMock()
        mock_db.session = mock_session

        with patch.dict('sys.modules', {
            'hermes_server.app': MagicMock(db=mock_db),
            'hermes_server.models.execution': MagicMock(),
            'hermes_server.models.test_case': MagicMock(TestCase=MagicMock()),
            'hermes_server.models.project': MagicMock(Environment=MagicMock(), GlobalVariable=MagicMock()),
        }):
            from hermes_worker.tasks.test_execution import execute_test_case
            result = execute_test_case(case_id=99999, environment_id=1)
            assert result is None

    @patch('hermes_worker.tasks.test_execution._get_app')
    def test_execute_test_case_nonexistent_environment(self, mock_get_app):
        mock_app = MagicMock()
        mock_get_app.return_value = mock_app

        mock_case = MagicMock()
        mock_session = MagicMock()
        mock_session.get.side_effect = [mock_case, None]

        mock_db = MagicMock()
        mock_db.session = mock_session

        with patch.dict('sys.modules', {
            'hermes_server.app': MagicMock(db=mock_db),
            'hermes_server.models.execution': MagicMock(),
            'hermes_server.models.test_case': MagicMock(TestCase=MagicMock()),
            'hermes_server.models.project': MagicMock(Environment=MagicMock(), GlobalVariable=MagicMock()),
        }):
            from hermes_worker.tasks.test_execution import execute_test_case
            result = execute_test_case(case_id=1, environment_id=99999)
            assert result is None


class TestExecuteTestSuiteLogic:
    @patch('hermes_worker.tasks.test_execution._get_app')
    def test_execute_test_suite_nonexistent_execution(self, mock_get_app):
        mock_app = MagicMock()
        mock_get_app.return_value = mock_app

        mock_session = MagicMock()
        mock_session.get.return_value = None

        mock_db = MagicMock()
        mock_db.session = mock_session

        with patch.dict('sys.modules', {
            'hermes_server.app': MagicMock(db=mock_db),
            'hermes_server.models.execution': MagicMock(TestExecution=MagicMock(), TestStepResult=MagicMock()),
            'hermes_server.models.test_case': MagicMock(TestCase=MagicMock(), TestSuite=MagicMock(), TestSuiteCase=MagicMock()),
            'hermes_server.models.project': MagicMock(Environment=MagicMock(), GlobalVariable=MagicMock()),
            'hermes_server.models.notification': MagicMock(NotificationConfig=MagicMock()),
        }):
            from hermes_worker.tasks.test_execution import execute_test_suite
            result = execute_test_suite(execution_id=99999, suite_id=1, environment_id=1)
            assert result is None


class TestExecuteScheduledTaskLogic:
    @patch('hermes_worker.tasks.test_execution._get_app')
    def test_execute_scheduled_task_disabled(self, mock_get_app):
        mock_app = MagicMock()
        mock_get_app.return_value = mock_app

        mock_task = MagicMock()
        mock_task.is_enabled = False

        mock_session = MagicMock()
        mock_session.get.return_value = mock_task

        mock_db = MagicMock()
        mock_db.session = mock_session

        with patch.dict('sys.modules', {
            'hermes_server.app': MagicMock(db=mock_db),
            'hermes_server.models.scheduled_task': MagicMock(ScheduledTask=MagicMock()),
            'hermes_server.models.execution': MagicMock(TestExecution=MagicMock()),
        }):
            from hermes_worker.tasks.test_execution import execute_scheduled_task
            result = execute_scheduled_task(scheduled_task_id=1)
            assert result is None
            assert not mock_session.add.called

    @patch('hermes_worker.tasks.test_execution._get_app')
    def test_execute_scheduled_task_nonexistent(self, mock_get_app):
        mock_app = MagicMock()
        mock_get_app.return_value = mock_app

        mock_session = MagicMock()
        mock_session.get.return_value = None

        mock_db = MagicMock()
        mock_db.session = mock_session

        with patch.dict('sys.modules', {
            'hermes_server.app': MagicMock(db=mock_db),
            'hermes_server.models.scheduled_task': MagicMock(ScheduledTask=MagicMock()),
            'hermes_server.models.execution': MagicMock(TestExecution=MagicMock()),
        }):
            from hermes_worker.tasks.test_execution import execute_scheduled_task
            result = execute_scheduled_task(scheduled_task_id=99999)
            assert result is None


class TestHeartbeatLogic:
    @patch('hermes_worker.tasks.heartbeat._get_redis_client')
    def test_heartbeat_writes_to_redis(self, mock_get_redis):
        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        from hermes_worker.tasks.heartbeat import heartbeat
        heartbeat()

        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        key = call_args[0][0]
        ttl = call_args[0][1]
        value = call_args[0][2]

        assert key.startswith("hermes:worker:heartbeat:")
        assert ttl == 60
        assert "worker_name" in value
        assert "status" in value
