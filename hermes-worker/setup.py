from setuptools import setup, find_packages

setup(
    name="hermes-worker",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "celery>=5.3",
        "redis>=5.0",
        "requests>=2.31",
        "pymysql>=1.1",
    ],
    description="Hermes Worker - Distributed task execution node",
)
