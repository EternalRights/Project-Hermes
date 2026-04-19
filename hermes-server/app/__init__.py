from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()


def create_app(config_name=None):
    from config.config import config

    app = Flask(__name__)

    if config_name is None:
        config_name = app.config.get('ENV', 'development')

    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    from api.v1 import api_v1
    app.register_blueprint(api_v1)

    from app.error_handlers import register_error_handlers
    register_error_handlers(app)

    from middleware.request_logger import register_request_logger
    register_request_logger(app)

    from app.metrics import setup_metrics
    setup_metrics(app)

    return app
