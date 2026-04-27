# src/notification_service/app.py
import logging

from .application.send_absence_alert_use_case import SendAbsenceAlertUseCase
from .domain.service.notification_service import NotificationService
from .infrastructure.adapters.inbound.rabbitmq_consumer import RabbitMQConsumer
from .infrastructure.adapters.outbound.postgres_notification_repository import (
    PostgresNotificationRepository,
)
from .infrastructure.adapters.outbound.smtp_email_sender import SMTPEmailSender
from .infrastructure.config.config import Settings
from .infrastructure.config.db_config import build_session_factory

logging.basicConfig(level=logging.INFO)


def run() -> None:
    settings = Settings.from_env()
    session_factory = build_session_factory(settings.notification_database_url)

    email_sender = SMTPEmailSender(
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_user=settings.smtp_user,
        smtp_password=settings.smtp_password,
    )
    repository = PostgresNotificationRepository(session_factory=session_factory)
    notification_service = NotificationService(
        email_sender=email_sender,
        repository=repository,
    )
    use_case = SendAbsenceAlertUseCase(notification_service=notification_service)

    consumer = RabbitMQConsumer(
        rabbitmq_url=settings.rabbitmq_url,
        use_case=use_case,
    )
    consumer.start_consuming()


if __name__ == "__main__":
    run()

