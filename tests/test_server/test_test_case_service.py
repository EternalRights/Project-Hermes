import pytest
from unittest.mock import patch, MagicMock

from hermes_server.services.test_case_service import TestCaseService
from hermes_server.services.exceptions import ValidationError, NotFoundError


class TestTestCaseServiceCreate:
    def test_create_missing_name(self):
        with pytest.raises(ValidationError, match='name and project_id are required'):
            TestCaseService.create_test_case({'project_id': 1}, user_id=1)

    def test_create_missing_project_id(self):
        with pytest.raises(ValidationError, match='name and project_id are required'):
            TestCaseService.create_test_case({'name': 'test'}, user_id=1)

    @patch('hermes_server.services.test_case_service.db')
    @patch('hermes_server.services.test_case_service.TestCase')
    def test_create_success(self, MockTestCase, mock_db):
        data = {'name': 'test case', 'project_id': 1}
        result = TestCaseService.create_test_case(data, user_id=1)
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()


class TestTestCaseServiceGet:
    @patch('hermes_server.services.test_case_service.db')
    def test_get_not_found(self, mock_db):
        mock_db.session.get.return_value = None
        with pytest.raises(NotFoundError, match='test case not found'):
            TestCaseService.get_test_case(999)

    @patch('hermes_server.services.test_case_service.db')
    def test_get_success(self, mock_db):
        mock_case = MagicMock()
        mock_db.session.get.return_value = mock_case
        result = TestCaseService.get_test_case(1)
        assert result == mock_case


class TestTestCaseServiceUpdate:
    @patch('hermes_server.services.test_case_service.db')
    def test_update_success(self, mock_db):
        mock_case = MagicMock()
        mock_case.name = 'old'
        mock_db.session.get.return_value = mock_case

        result = TestCaseService.update_test_case(1, {'name': 'new'})
        assert result == mock_case
        mock_db.session.commit.assert_called_once()


class TestTestCaseServiceDelete:
    @patch('hermes_server.services.test_case_service.db')
    def test_delete_success(self, mock_db):
        mock_case = MagicMock()
        mock_db.session.get.return_value = mock_case

        TestCaseService.delete_test_case(1)
        mock_db.session.delete.assert_called_once_with(mock_case)
        mock_db.session.commit.assert_called_once()


class TestTestCaseServiceModules:
    def test_get_modules_missing_project_id(self):
        with pytest.raises(ValidationError, match='project_id is required'):
            TestCaseService.get_modules(None)


class TestTestCaseServiceTags:
    def test_get_tags_missing_project_id(self):
        with pytest.raises(ValidationError, match='project_id is required'):
            TestCaseService.get_tags(None)


class TestTestCaseServiceExport:
    def test_export_missing_project_id(self):
        with pytest.raises(ValidationError, match='project_id is required'):
            TestCaseService.export_test_cases(None)


class TestTestCaseServiceImport:
    def test_import_missing_project_id(self):
        with pytest.raises(ValidationError, match='project_id and cases are required'):
            TestCaseService.import_test_cases(None, [{'name': 'test'}], user_id=1)

    def test_import_invalid_cases(self):
        with pytest.raises(ValidationError, match='project_id and cases are required'):
            TestCaseService.import_test_cases(1, 'not_a_list', user_id=1)
