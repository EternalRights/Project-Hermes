import pytest
from unittest.mock import patch, MagicMock

from hermes_server.services.exceptions import (
    NotFoundError,
    ValidationError,
    DuplicateError,
    AuthenticationError,
    AuthorizationError,
)
from hermes_server.app.error_handlers import HermesBusinessError


class TestNotFoundError:
    def test_default_message(self):
        err = NotFoundError()
        assert err.message == 'resource not found'
        assert err.code == 404

    def test_custom_message(self):
        err = NotFoundError('test case not found')
        assert err.message == 'test case not found'
        assert err.code == 404


class TestValidationError:
    def test_default_message(self):
        err = ValidationError()
        assert err.message == 'validation error'
        assert err.code == 400

    def test_custom_message(self):
        err = ValidationError('name is required')
        assert err.message == 'name is required'
        assert err.code == 400


class TestDuplicateError:
    def test_default_message(self):
        err = DuplicateError()
        assert err.message == 'resource already exists'
        assert err.code == 409


class TestAuthenticationError:
    def test_default_message(self):
        err = AuthenticationError()
        assert err.message == 'authentication failed'
        assert err.code == 401


class TestAuthorizationError:
    def test_default_message(self):
        err = AuthorizationError()
        assert err.message == 'permission denied'
        assert err.code == 403


class TestHermesBusinessErrorInheritance:
    def test_all_exceptions_inherit_from_base(self):
        assert issubclass(NotFoundError, HermesBusinessError)
        assert issubclass(ValidationError, HermesBusinessError)
        assert issubclass(DuplicateError, HermesBusinessError)
        assert issubclass(AuthenticationError, HermesBusinessError)
        assert issubclass(AuthorizationError, HermesBusinessError)
