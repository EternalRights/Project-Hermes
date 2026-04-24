from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_server.services.auth_service import AuthService
from hermes_server.app.response import success_response, error_response
from hermes_server.app.error_handlers import HermesBusinessError

bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@bp.route('/register', methods=['POST'])
def register():
    body = request.get_json(silent=True) or {}
    try:
        user = AuthService.register(
            username=body.get('username'),
            email=body.get('email'),
            password=body.get('password'),
        )
        return jsonify(success_response(data=user.to_dict(), message='registered', code=201)), 201
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/login', methods=['POST'])
def login():
    body = request.get_json(silent=True) or {}
    try:
        result = AuthService.login(
            username=body.get('username'),
            password=body.get('password'),
        )
        return jsonify(success_response(data=result)), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    try:
        result = AuthService.refresh_token(user_id)
        return jsonify(success_response(data=result)), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_info():
    current_user_id = get_jwt_identity()
    try:
        data = AuthService.get_current_user(current_user_id)
        return jsonify(success_response(data=data)), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code
