from flask_jwt_extended import create_access_token, create_refresh_token

from hermes_server.app import db
from hermes_server.models.user import User, Role
from hermes_server.services.exceptions import ValidationError, AuthenticationError, NotFoundError


class AuthService:
    @staticmethod
    def register(username, email, password):
        if not username or not email or not password:
            raise ValidationError('username, email and password are required')

        if User.query.filter_by(username=username).first():
            raise ValidationError('username already exists')

        if User.query.filter_by(email=email).first():
            raise ValidationError('email already exists')

        user = User(username=username, email=email)
        user.set_password(password)

        role = Role.query.filter_by(name='test_engineer').first()
        if role:
            user.roles.append(role)

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def login(username, password):
        if not username or not password:
            raise ValidationError('username and password are required')

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            raise AuthenticationError('invalid username or password')

        if not user.is_active:
            raise AuthenticationError('user is inactive')

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token': access_token,
            'refreshToken': refresh_token,
            'user': user.to_dict(),
        }

    @staticmethod
    def refresh_token(user_id):
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundError('user not found')

        access_token = create_access_token(identity=user_id)
        return {'access_token': access_token}

    @staticmethod
    def get_current_user(user_id):
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundError('user not found')
        return user.to_dict(include_roles=True)
