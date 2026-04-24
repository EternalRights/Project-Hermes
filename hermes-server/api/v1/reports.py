from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from hermes_server.services.report_service import ReportService
from hermes_server.app.response import success_response, error_response
from hermes_server.app.error_handlers import HermesBusinessError
from hermes_server.middleware.permission import require_permission

bp = Blueprint('reports', __name__, url_prefix='/api/v1/reports')


@bp.route('/<int:execution_id>', methods=['GET'])
@jwt_required()
@require_permission('report:read')
def get_report(execution_id):
    try:
        data = ReportService.get_report(execution_id)
        return success_response(data=data), 200
    except HermesBusinessError as e:
        return error_response(message=e.message, code=e.code), e.code


@bp.route('/trend', methods=['GET'])
@jwt_required()
@require_permission('report:read')
def get_trend():
    suite_id = request.args.get('suite_id', type=int)
    days = request.args.get('days', 30, type=int)

    try:
        data = ReportService.get_trend(suite_id, days)
        return success_response(data=data), 200
    except HermesBusinessError as e:
        return error_response(message=e.message, code=e.code), e.code


@bp.route('/<int:execution_id>/export', methods=['GET'])
@jwt_required()
@require_permission('report:read')
def export_report(execution_id):
    try:
        return ReportService.export_report_html(execution_id)
    except HermesBusinessError as e:
        return error_response(message=e.message, code=e.code), e.code
