from setuptools import setup, find_packages

setup(
    name="hermes-core",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31",
        "jsonschema>=4.20",
        "jsonpath-ng>=1.6",
        "pydantic>=2.5",
        "pymysql>=1.1",
    ],
    description="Hermes Core - High-performance API test engine",
)
