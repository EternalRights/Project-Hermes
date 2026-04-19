import time
import logging

logger = logging.getLogger('hermes.request')


def register_request_logger(app):
    @app.before_request
    def before_request():
        from flask import g
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        from flask import g, request
        duration = time.time() - getattr(g, 'start_time', time.time())
        logger.info(
            '%s %s %s %.3fs',
            request.method,
            request.path,
            response.status_code,
            duration,
        )
        return response
