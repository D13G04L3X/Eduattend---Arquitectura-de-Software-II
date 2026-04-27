# src/notification_service/infrastructure/config/config.py
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    rabbitmq_url: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    notification_database_url: str

    @staticmethod
    def from_env() -> "Settings":
        return Settings(
            rabbitmq_url=os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/"),
            smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_user=os.getenv("SMTP_USER", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            notification_database_url=os.getenv(
                "NOTIFICATION_DATABASE_URL",
                "postgresql+psycopg2://notifications_user:notifications_password@postgres_notifications:5432/notifications_db",
            ),
        )
