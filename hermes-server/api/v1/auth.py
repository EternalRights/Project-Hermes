from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

from hermes_server.app import db
from hermes_server.models.user import User, Role, Permission
from hermes_server.app.response import success_response, error_response

bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@bp.route('/register', methods=['POST'])
def register():
    body = request.get_json(silent=True) or {}
    username = body.get('username')
    email = body.get('email')
    password = body.get('password')

    if not username or not email or not password:
        return error_response(message='username, email and password are required', code=400), 400

    if User.query.filter_by(username=username).first():
        return error_response(message='username already exists', code=400), 400

    if User.query.filter_by(email=email).first():
        return error_response(message='email already exists', code=400), 400

    user = User(username=username, email=email)
    user.set_password(password)

    role = Role.query.filter_by(name='test_engineer').first()
    if role:
        user.roles.append(role)

    db.session.add(user)
    db.session.commit()

    return success_response(data={
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat() if user.created_at else None,
    }, message='registered', code=201), 201


@bp.route('/login', methods=['POST'])
def login():
    body = request.get_json(silent=True) or {}
    username = body.get('username')
    password = body.get('password')

    if not username or not password:
        return error_response(message='username and password are required', code=400), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return error_response(message='invalid username or password', code=401), 401

    if not user.is_active:
        return error_response(message='user is inactive', code=403), 403

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return success_response(data={
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token': access_token,
        'refreshToken': refresh_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active,
        },
    }), 200


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return success_response(data={'access_token': access_token}), 200


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_info():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    if not user:
        return jsonify(error_response('User not found', 404)), 404
    roles = [{'id': r.id, 'name': r.name} for r in user.roles]
    return jsonify(success_response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'roles': roles,
    })), 200
