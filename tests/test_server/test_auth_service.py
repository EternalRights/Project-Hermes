import pytest
from unittest.mock import patch, MagicMock

from hermes_server.services.auth_service import AuthService
from hermes_server.services.exceptions import ValidationError, AuthenticationError, NotFoundError


class TestAuthServiceRegister:
    def test_register_missing_fields(self):
        with pytest.raises(ValidationError, match='username, email and password are required'):
            AuthService.register(None, 'test@test.com', 'pass')
        with pytest.raises(ValidationError, match='username, email and password are required'):
            AuthService.register('user', None, 'pass')
        with pytest.raises(ValidationError, match='username, email and password are required'):
            AuthService.register('user', 'test@test.com', None)

    @patch('hermes_server.services.auth_service.User')
    @patch('hermes_server.services.auth_service.db')
    def test_register_duplicate_username(self, mock_db, MockUser):
        MockUser.query.filter_by.return_value.first.return_value = MagicMock()
        with pytest.raises(ValidationError, match='username already exists'):
            AuthService.register('existing', 'new@test.com', 'pass')

    @patch('hermes_server.services.auth_service.User')
    @patch('hermes_server.services.auth_service.Role')
    @patch('hermes_server.services.auth_service.db')
    def test_register_success(self, mock_db, MockRole, MockUser):
        MockUser.query.filter_by.return_value.first.return_value = None
        MockRole.query.filter_by.return_value.first.return_value = None

        user = AuthService.register('newuser', 'new@test.com', 'password123')
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()


class TestAuthServiceLogin:
    def test_login_missing_fields(self):
        with pytest.raises(ValidationError, match='username and password are required'):
            AuthService.login(None, 'pass')
        with pytest.raises(ValidationError, match='username and password are required'):
            AuthService.login('user', None)

    @patch('hermes_server.services.auth_service.User')
    def test_login_invalid_credentials(self, MockUser):
        MockUser.query.filter_by.return_value.first.return_value = None
        with pytest.raises(AuthenticationError, match='invalid username or password'):
            AuthService.login('user', 'wrong')

    @patch('hermes_server.services.auth_service.User')
    def test_login_inactive_user(self, MockUser):
        mock_user = MagicMock()
        mock_user.check_password.return_value = True
        mock_user.is_active = False
        MockUser.query.filter_by.return_value.first.return_value = mock_user
        with pytest.raises(AuthenticationError, match='user is inactive'):
            AuthService.login('user', 'pass')

    @patch('hermes_server.services.auth_service.create_refresh_token')
    @patch('hermes_server.services.auth_service.create_access_token')
    @patch('hermes_server.services.auth_service.User')
    def test_login_success(self, MockUser, mock_access, mock_refresh):
        mock_user = MagicMock()
        mock_user.check_password.return_value = True
        mock_user.is_active = True
        mock_user.id = 1
        mock_user.to_dict.return_value = {'id': 1, 'username': 'user'}
        MockUser.query.filter_by.return_value.first.return_value = mock_user
        mock_access.return_value = 'access_token'
        mock_refresh.return_value = 'refresh_token'

        result = AuthService.login('user', 'pass')
        assert result['access_token'] == 'access_token'
        assert result['refresh_token'] == 'refresh_token'


class TestAuthServiceRefresh:
    @patch('hermes_server.services.auth_service.db')
    def test_refresh_user_not_found(self, mock_db):
        mock_db.session.get.return_value = None
        with pytest.raises(NotFoundError, match='user not found'):
            AuthService.refresh_token(999)

    @patch('hermes_server.services.auth_service.create_access_token')
    @patch('hermes_server.services.auth_service.db')
    def test_refresh_success(self, mock_db, mock_access):
        mock_db.session.get.return_value = MagicMock()
        mock_access.return_value = 'new_access_token'

        result = AuthService.refresh_token(1)
        assert result['access_token'] == 'new_access_token'
