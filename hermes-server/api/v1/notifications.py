from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_server.services.notification_service import NotificationService
from hermes_server.app.response import success_response, error_response, paginate_response
from hermes_server.app.error_handlers import HermesBusinessError
from hermes_server.middleware.permission import require_permission

bp = Blueprint('notifications', __name__, url_prefix='/api/v1/notifications')


@bp.route('', methods=['GET'])
@jwt_required()
@require_permission('notification:read')
def get_notifications():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    project_id = request.args.get('project_id', type=int)

    query = NotificationService.list_notifications(page=page, per_page=per_page, project_id=project_id)
    data = paginate_response(query, page, per_page)
    items = [item.to_dict() for item in data.pop('items')]
    return jsonify(success_response(data={**data, 'items': items})), 200


@bp.route('', methods=['POST'])
@jwt_required()
@require_permission('notification:create')
def create_notification():
    body = request.get_json(silent=True) or {}

    try:
        notification = NotificationService.create_notification(body)
        return jsonify(success_response(data=notification.to_dict(), message='created', code=201)), 201
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:notification_id>', methods=['GET'])
@jwt_required()
@require_permission('notification:read')
def get_notification(notification_id):
    try:
        notification = NotificationService.get_notification(notification_id)
        return jsonify(success_response(data=notification.to_dict())), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:notification_id>', methods=['PUT'])
@jwt_required()
@require_permission('notification:update')
def update_notification(notification_id):
    body = request.get_json(silent=True) or {}

    try:
        notification = NotificationService.update_notification(notification_id, body)
        return jsonify(success_response(data=notification.to_dict(), message='updated')), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
@require_permission('notification:delete')
def delete_notification(notification_id):
    try:
        NotificationService.delete_notification(notification_id)
        return jsonify(success_response(message='deleted')), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code


@bp.route('/<int:notification_id>/test', methods=['POST'])
@jwt_required()
@require_permission('notification:update')
def test_notification(notification_id):
    try:
        result = NotificationService.test_notification(notification_id)
        return jsonify(success_response(data=result, message='test notification sent')), 200
    except HermesBusinessError as e:
        return jsonify(error_response(message=e.message, code=e.code)), e.code
    except Exception as e:
        return jsonify(error_response(message=f'test notification failed: {str(e)}', code=500)), 500
