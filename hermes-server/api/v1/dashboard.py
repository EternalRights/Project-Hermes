from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from hermes_server.app import db
from hermes_server.app.response import success_response, error_response
from hermes_server.models.execution import TestExecution
from hermes_server.models.test_case import TestCase, TestSuite
from sqlalchemy import func
from datetime import datetime, timezone

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/v1/dashboard')


@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    today_executions = TestExecution.query.filter(
        TestExecution.created_at >= today_start
    ).count()

    total_passed = TestExecution.query.filter(
        TestExecution.status == 'success',
        TestExecution.created_at >= today_start
    ).count()

    pass_rate = round((total_passed / today_executions * 100) if today_executions > 0 else 0, 2)

    active_cases = TestCase.query.filter(TestCase.status == 'active').count()
    active_suites = TestSuite.query.count()

    recent = TestExecution.query.order_by(TestExecution.created_at.desc()).limit(10).all()
    recent_list = [{
        'id': e.id,
        'status': e.status,
        'created_at': e.created_at.isoformat() if e.created_at else None,
        'duration': e.duration,
    } for e in recent]

    return jsonify(success_response({
        'todayExecutions': today_executions,
        'passRate': pass_rate,
        'activeCases': active_cases,
        'activeSuites': active_suites,
        'recentExecutions': recent_list,
    })), 200
