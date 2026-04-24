import pytest
from unittest.mock import patch, MagicMock

from hermes_server.services.project_service import ProjectService
from hermes_server.services.exceptions import ValidationError, NotFoundError


class TestProjectServiceCreate:
    def test_create_project_missing_name(self):
        with pytest.raises(ValidationError, match='name is required'):
            ProjectService.create_project(name=None)

    @patch('hermes_server.services.project_service.db')
    @patch('hermes_server.services.project_service.Project')
    def test_create_project_success(self, MockProject, mock_db):
        project = ProjectService.create_project(name='Test Project', description='desc', owner_id=1)
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()


class TestProjectServiceGet:
    @patch('hermes_server.services.project_service.db')
    def test_get_project_not_found(self, mock_db):
        mock_db.session.get.return_value = None
        with pytest.raises(NotFoundError, match='project not found'):
            ProjectService.get_project(999)

    @patch('hermes_server.services.project_service.db')
    def test_get_project_inactive(self, mock_db):
        mock_project = MagicMock()
        mock_project.is_active = False
        mock_db.session.get.return_value = mock_project
        with pytest.raises(NotFoundError, match='project not found'):
            ProjectService.get_project(1)

    @patch('hermes_server.services.project_service.db')
    def test_get_project_success(self, mock_db):
        mock_project = MagicMock()
        mock_project.is_active = True
        mock_db.session.get.return_value = mock_project
        result = ProjectService.get_project(1)
        assert result == mock_project


class TestProjectServiceUpdate:
    @patch('hermes_server.services.project_service.db')
    def test_update_project_success(self, mock_db):
        mock_project = MagicMock()
        mock_project.is_active = True
        mock_db.session.get.return_value = mock_project

        result = ProjectService.update_project(1, name='Updated', description='new desc')
        assert result == mock_project
        mock_db.session.commit.assert_called_once()


class TestProjectServiceDelete:
    @patch('hermes_server.services.project_service.db')
    def test_delete_project_success(self, mock_db):
        mock_project = MagicMock()
        mock_project.is_active = True
        mock_db.session.get.return_value = mock_project

        ProjectService.delete_project(1)
        assert mock_project.is_active is False
        mock_db.session.commit.assert_called_once()


class TestProjectServiceList:
    @patch('hermes_server.services.project_service.Project')
    def test_list_projects_with_name_filter(self, MockProject):
        mock_query = MagicMock()
        MockProject.query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query

        result = ProjectService.list_projects(name='test')
        assert result == mock_query

    @patch('hermes_server.services.project_service.Project')
    def test_list_projects_no_filter(self, MockProject):
        mock_query = MagicMock()
        MockProject.query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query

        result = ProjectService.list_projects()
        assert result == mock_query
