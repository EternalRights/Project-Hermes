from flask import jsonify
from app.response import error_response


class HermesBusinessError(Exception):
    def __init__(self, message='业务异常', code=400, data=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(error_response(message='Bad Request', code=400)), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify(error_response(message='Unauthorized', code=401)), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify(error_response(message='Forbidden', code=403)), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(error_response(message='Not Found', code=404)), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify(error_response(message='Internal Server Error', code=500)), 500

    @app.errorhandler(HermesBusinessError)
    def handle_business_error(error):
        return jsonify(error_response(message=error.message, code=error.code, data=error.data)), error.code
