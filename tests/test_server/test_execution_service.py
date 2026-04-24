import pytest
from unittest.mock import patch, MagicMock

from hermes_server.services.execution_service import ExecutionService
from hermes_server.services.exceptions import ValidationError, NotFoundError


class TestExecutionServiceCreate:
    def test_create_missing_suite_id(self):
        with pytest.raises(ValidationError, match='suite_id and environment_id are required'):
            ExecutionService.create_execution({'environment_id': 1}, user_id=1)

    def test_create_missing_environment_id(self):
        with pytest.raises(ValidationError, match='suite_id and environment_id are required'):
            ExecutionService.create_execution({'suite_id': 1}, user_id=1)

    @patch('hermes_server.services.execution_service.db')
    @patch('hermes_server.services.execution_service.TestSuite')
    def test_create_suite_not_found(self, MockSuite, mock_db):
        MockSuite.query.session.get.return_value = None
        mock_db.session.get.return_value = None
        with pytest.raises(NotFoundError, match='test suite not found'):
            ExecutionService.create_execution({'suite_id': 999, 'environment_id': 1}, user_id=1)

    @patch('hermes_server.services.execution_service.db')
    @patch('hermes_server.services.execution_service.TestSuite')
    def test_create_success(self, MockSuite, mock_db):
        mock_suite = MagicMock()
        mock_db.session.get.return_value = mock_suite

        result = ExecutionService.create_execution({'suite_id': 1, 'environment_id': 1}, user_id=1)
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()


class TestExecutionServiceGet:
    @patch('hermes_server.services.execution_service.db')
    def test_get_not_found(self, mock_db):
        mock_db.session.get.return_value = None
        with pytest.raises(NotFoundError, match='execution not found'):
            ExecutionService.get_execution(999)

    @patch('hermes_server.services.execution_service.db')
    def test_get_success(self, mock_db):
        mock_execution = MagicMock()
        mock_db.session.get.return_value = mock_execution
        result = ExecutionService.get_execution(1)
        assert result == mock_execution


class TestExecutionServiceList:
    @patch('hermes_server.services.execution_service.TestExecution')
    def test_list_with_filters(self, MockExecution):
        mock_query = MagicMock()
        MockExecution.query = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query

        result = ExecutionService.list_executions(suite_id=1, status='running')
        assert result == mock_query
