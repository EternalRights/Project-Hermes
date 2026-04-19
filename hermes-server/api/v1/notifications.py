import smtplib
from email.mime.text import MIMEText

import requests
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_server.app import db
from hermes_server.app.response import success_response, error_response, paginate_response
from hermes_server.models.notification import NotificationConfig

bp = Blueprint('notifications', __name__, url_prefix='/api/v1/notifications')


@bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    project_id = request.args.get('project_id', type=int)

    query = NotificationConfig.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    query = query.order_by(NotificationConfig.created_at.desc())

    data = paginate_response(query, page, per_page)
    items = []
    for item in data.pop('items'):
        items.append({
            'id': item.id,
            'name': item.name,
            'project_id': item.project_id,
            'type': item.type,
            'config': item.config,
            'trigger_condition': item.trigger_condition,
            'is_enabled': item.is_enabled,
            'created_at': item.created_at.isoformat() if item.created_at else None,
            'updated_at': item.updated_at.isoformat() if item.updated_at else None,
        })

    return success_response(data={**data, 'items': items}), 200


@bp.route('', methods=['POST'])
@jwt_required()
def create_notification():
    body = request.get_json(silent=True) or {}

    name = body.get('name')
    project_id = body.get('project_id')
    notif_type = body.get('type')
    config = body.get('config')
    trigger_condition = body.get('trigger_condition')
    is_enabled = body.get('is_enabled', True)

    if not all([name, project_id, notif_type]):
        return error_response(message='name, project_id, type are required', code=400), 400

    notification = NotificationConfig(
        name=name,
        project_id=project_id,
        type=notif_type,
        config=config,
        trigger_condition=trigger_condition,
        is_enabled=is_enabled,
    )
    db.session.add(notification)
    db.session.commit()

    return success_response(data={
        'id': notification.id,
        'name': notification.name,
        'project_id': notification.project_id,
        'type': notification.type,
        'config': notification.config,
        'trigger_condition': notification.trigger_condition,
        'is_enabled': notification.is_enabled,
        'created_at': notification.created_at.isoformat() if notification.created_at else None,
    }, message='created', code=201), 201


@bp.route('/<int:notification_id>', methods=['GET'])
@jwt_required()
def get_notification(notification_id):
    notification = NotificationConfig.query.get(notification_id)
    if not notification:
        return error_response(message='notification not found', code=404), 404

    return success_response(data={
        'id': notification.id,
        'name': notification.name,
        'project_id': notification.project_id,
        'type': notification.type,
        'config': notification.config,
        'trigger_condition': notification.trigger_condition,
        'is_enabled': notification.is_enabled,
        'created_at': notification.created_at.isoformat() if notification.created_at else None,
        'updated_at': notification.updated_at.isoformat() if notification.updated_at else None,
    }), 200


@bp.route('/<int:notification_id>', methods=['PUT'])
@jwt_required()
def update_notification(notification_id):
    notification = NotificationConfig.query.get(notification_id)
    if not notification:
        return error_response(message='notification not found', code=404), 404

    body = request.get_json(silent=True) or {}

    if 'name' in body:
        notification.name = body['name']
    if 'project_id' in body:
        notification.project_id = body['project_id']
    if 'type' in body:
        notification.type = body['type']
    if 'config' in body:
        notification.config = body['config']
    if 'trigger_condition' in body:
        notification.trigger_condition = body['trigger_condition']
    if 'is_enabled' in body:
        notification.is_enabled = body['is_enabled']

    db.session.commit()

    return success_response(data={
        'id': notification.id,
        'name': notification.name,
        'project_id': notification.project_id,
        'type': notification.type,
        'config': notification.config,
        'trigger_condition': notification.trigger_condition,
        'is_enabled': notification.is_enabled,
        'created_at': notification.created_at.isoformat() if notification.created_at else None,
        'updated_at': notification.updated_at.isoformat() if notification.updated_at else None,
    }, message='updated'), 200


@bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    notification = NotificationConfig.query.get(notification_id)
    if not notification:
        return error_response(message='notification not found', code=404), 404

    db.session.delete(notification)
    db.session.commit()

    return success_response(message='deleted'), 200


@bp.route('/<int:notification_id>/test', methods=['POST'])
@jwt_required()
def test_notification(notification_id):
    notification = NotificationConfig.query.get(notification_id)
    if not notification:
        return error_response(message='notification not found', code=404), 404

    config = notification.config or {}
    notif_type = notification.type

    try:
        if notif_type == 'webhook':
            url = config.get('url')
            if not url:
                return error_response(message='webhook url is required', code=400), 400
            headers = config.get('headers', {})
            body = config.get('body', {'message': 'Hermes test notification'})
            resp = requests.post(url, json=body, headers=headers, timeout=10)
            return success_response(data={
                'status_code': resp.status_code,
                'response': resp.text[:500],
            }, message='test notification sent'), 200

        elif notif_type == 'email':
            smtp_host = config.get('smtp_host')
            smtp_port = config.get('smtp_port', 25)
            sender = config.get('sender')
            receiver = config.get('receiver')
            if not all([smtp_host, sender, receiver]):
                return error_response(message='smtp_host, sender, receiver are required', code=400), 400

            msg = MIMEText('Hermes test notification')
            msg['Subject'] = 'Hermes Test Notification'
            msg['From'] = sender
            msg['To'] = receiver

            smtp_user = config.get('smtp_user')
            smtp_password = config.get('smtp_password')
            use_tls = config.get('use_tls', True)

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if use_tls:
                    server.starttls()
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                server.sendmail(sender, [receiver], msg.as_string())

            return success_response(message='test email sent'), 200

        elif notif_type in ('wechat', 'dingtalk'):
            url = config.get('url')
            if not url:
                return error_response(message=f'{notif_type} webhook url is required', code=400), 400
            body = config.get('body', {
                'msgtype': 'text',
                'text': {'content': 'Hermes test notification'},
            })
            resp = requests.post(url, json=body, timeout=10)
            return success_response(data={
                'status_code': resp.status_code,
                'response': resp.text[:500],
            }, message=f'test {notif_type} notification sent'), 200

        else:
            return error_response(message=f'unsupported notification type: {notif_type}', code=400), 400

    except Exception as e:
        return error_response(message=f'test notification failed: {str(e)}', code=500), 500
