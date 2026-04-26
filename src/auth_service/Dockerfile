# src/auth_service/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy psycopg2-binary PyJWT bcrypt redis email-validator

ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["uvicorn", "src.auth_service.app:app", "--host", "0.0.0.0", "--port", "8001"]
