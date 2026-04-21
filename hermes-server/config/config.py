import os
from datetime import timedelta

DEFAULT_SECRET_KEY = 'hermes-secret-key'
DEFAULT_JWT_SECRET_KEY = 'hermes-jwt-secret-key'


def _validate_production_secrets():
    flask_env = os.environ.get('FLASK_ENV', 'development')
    if flask_env == 'production':
        secret_key = os.environ.get('SECRET_KEY', DEFAULT_SECRET_KEY)
        jwt_secret_key = os.environ.get('JWT_SECRET_KEY', DEFAULT_JWT_SECRET_KEY)
        if secret_key == DEFAULT_SECRET_KEY:
            raise RuntimeError("SECRET_KEY must not be the default value in production")
        if jwt_secret_key == DEFAULT_JWT_SECRET_KEY:
            raise RuntimeError("JWT_SECRET_KEY must not be the default value in production")


_validate_production_secrets()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', DEFAULT_SECRET_KEY)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', DEFAULT_JWT_SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost:3306/hermes_dev'
    REDIS_URL = 'redis://localhost:6379/0'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    REDIS_URL = 'redis://localhost:6379/1'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    REDIS_URL = os.environ.get('REDIS_URL')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
