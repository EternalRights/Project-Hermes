from flask_jwt_extended import get_jwt_identity

from hermes_server.app import db
from hermes_server.models.user import User


def get_current_user():
    user_id = get_jwt_identity()
    return db.session.get(User, user_id)
