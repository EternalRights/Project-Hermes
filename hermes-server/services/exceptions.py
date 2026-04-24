from hermes_server.app.error_handlers import HermesBusinessError


class NotFoundError(HermesBusinessError):
    def __init__(self, message='resource not found'):
        super().__init__(message=message, code=404)


class ValidationError(HermesBusinessError):
    def __init__(self, message='validation error'):
        super().__init__(message=message, code=400)


class DuplicateError(HermesBusinessError):
    def __init__(self, message='resource already exists'):
        super().__init__(message=message, code=409)


class AuthenticationError(HermesBusinessError):
    def __init__(self, message='authentication failed'):
        super().__init__(message=message, code=401)


class AuthorizationError(HermesBusinessError):
    def __init__(self, message='permission denied'):
        super().__init__(message=message, code=403)
