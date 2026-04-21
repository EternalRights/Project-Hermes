from flask import Blueprint, jsonify
from app import db

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    try:
        db.session.execute(db.text('SELECT 1'))
        db_status = 'connected'
    except Exception:
        db_status = 'disconnected'

    if db_status == 'connected':
        return jsonify({'status': 'healthy', 'version': '1.0.0', 'database': db_status}), 200
    else:
        return jsonify({'status': 'unhealthy', 'version': '1.0.0', 'database': db_status}), 503
