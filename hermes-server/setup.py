from setuptools import setup, find_packages

setup(
    name="hermes-server",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "flask>=2.3",
        "flask-sqlalchemy>=3.0",
        "flask-migrate>=4.0",
        "flask-jwt-extended>=4.5",
        "flask-cors>=4.0",
        "pymysql>=1.1",
        "redis>=5.0",
        "celery>=5.3",
        "gunicorn>=21.2",
        "marshmallow>=3.20",
        "jsonschema>=4.20",
        "requests>=2.31",
        "prometheus-flask-instrumentator>=6.1",
    ],
    description="Hermes Server - API and management backend",
)
