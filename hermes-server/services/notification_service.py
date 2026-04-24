import smtplib
from email.mime.text import MIMEText

import requests

from hermes_server.app import db
from hermes_server.models.notification import NotificationConfig
from hermes_server.services.exceptions import ValidationError, NotFoundError


class NotificationService:
    @staticmethod
    def list_notifications(page=1, per_page=10, project_id=None):
        query = NotificationConfig.query
        if project_id:
            query = query.filter_by(project_id=project_id)
        query = query.order_by(NotificationConfig.created_at.desc())
        return query

    @staticmethod
    def create_notification(data):
        name = data.get('name')
        project_id = data.get('project_id')
        notif_type = data.get('type')

        if not all([name, project_id, notif_type]):
            raise ValidationError('name, project_id, type are required')

        notification = NotificationConfig(
            name=name,
            project_id=project_id,
            type=notif_type,
            config=data.get('config'),
            trigger_condition=data.get('trigger_condition'),
            is_enabled=data.get('is_enabled', True),
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def get_notification(notification_id):
        notification = db.session.get(NotificationConfig, notification_id)
        if not notification:
            raise NotFoundError('notification not found')
        return notification

    @staticmethod
    def update_notification(notification_id, data):
        notification = NotificationService.get_notification(notification_id)

        updatable_fields = ['name', 'project_id', 'type', 'config', 'trigger_condition', 'is_enabled']
        for field in updatable_fields:
            if field in data:
                setattr(notification, field, data[field])

        db.session.commit()
        return notification

    @staticmethod
    def delete_notification(notification_id):
        notification = NotificationService.get_notification(notification_id)
        db.session.delete(notification)
        db.session.commit()

    @staticmethod
    def test_notification(notification_id):
        notification = NotificationService.get_notification(notification_id)

        config = notification.config or {}
        notif_type = notification.type

        if notif_type == 'webhook':
            return NotificationService._test_webhook(config)
        elif notif_type == 'email':
            return NotificationService._test_email(config)
        elif notif_type in ('wechat', 'dingtalk'):
            return NotificationService._test_im(config, notif_type)
        else:
            raise ValidationError(f'unsupported notification type: {notif_type}')

    @staticmethod
    def _test_webhook(config):
        url = config.get('url')
        if not url:
            raise ValidationError('webhook url is required')
        headers = config.get('headers', {})
        body = config.get('body', {'message': 'Hermes test notification'})
        resp = requests.post(url, json=body, headers=headers, timeout=10)
        return {
            'status_code': resp.status_code,
            'response': resp.text[:500],
        }

    @staticmethod
    def _test_email(config):
        smtp_host = config.get('smtp_host')
        smtp_port = config.get('smtp_port', 25)
        sender = config.get('sender')
        receiver = config.get('receiver')
        if not all([smtp_host, sender, receiver]):
            raise ValidationError('smtp_host, sender, receiver are required')

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

        return {'message': 'test email sent'}

    @staticmethod
    def _test_im(config, notif_type):
        url = config.get('url')
        if not url:
            raise ValidationError(f'{notif_type} webhook url is required')
        body = config.get('body', {
            'msgtype': 'text',
            'text': {'content': 'Hermes test notification'},
        })
        resp = requests.post(url, json=body, timeout=10)
        return {
            'status_code': resp.status_code,
            'response': resp.text[:500],
        }
