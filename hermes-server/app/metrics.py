from prometheus_client import Counter, Histogram
from prometheus_flask_instrumentator import FlaskInstrumentator

hermes_test_execution_total = Counter(
    'hermes_test_execution_total',
    'Total test executions',
    ['status']
)

hermes_test_duration_seconds = Histogram(
    'hermes_test_duration_seconds',
    'Test execution duration',
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60, 120]
)

hermes_test_case_result_total = Counter(
    'hermes_test_case_result_total',
    'Test case results',
    ['status']
)


def setup_metrics(app):
    instrumentator = FlaskInstrumentator()
    instrumentator.init_app(app)
    instrumentator.expose(app, endpoint='/metrics', include_in_schema=False)
