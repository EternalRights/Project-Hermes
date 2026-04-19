FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD celery -A hermes_worker.celery_app:celery_app inspect ping || exit 1

CMD ["celery", "-A", "hermes_worker.celery_app:celery_app", "worker", "--loglevel=info", "--concurrency=4"]
