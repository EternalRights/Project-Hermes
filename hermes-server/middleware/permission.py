from functools import wraps

from hermes_server.app.response import error_response
from hermes_server.middleware.auth import get_current_user


def require_permission(*permission_codes):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return error_response(message='user not found', code=401), 401

            for code in permission_codes:
                if not user.has_permission(code):
                    return error_response(message='permission denied', code=403), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
