# src/notification_service/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir pika sqlalchemy psycopg2-binary

ENV PYTHONPATH=/app

CMD ["python", "-m", "src.notification_service.app"]

