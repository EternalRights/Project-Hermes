from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from hermes_server.services.dashboard_service import DashboardService
from hermes_server.app.response import success_response

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/v1/dashboard')


@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    data = DashboardService.get_stats()
    return jsonify(success_response(data)), 200
