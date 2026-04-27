# src/notification_service/domain/service/notification_service.py
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from ..exception.notification_exceptions import EmailSendError
from ..model.notification import Notification


class IEmailSender(Protocol):
    def send(self, to_email: str, subject: str, body: str) -> None: ...


class INotificationRepository(Protocol):
    def save(self, notification: Notification) -> Notification: ...


class NotificationService:
    def __init__(
        self,
        email_sender: IEmailSender,
        repository: INotificationRepository,
    ) -> None:
        self._email_sender = email_sender
        self._repository = repository

    def send_notification(self, student_email: str, subject: str, message: str) -> Notification:
        sent_at = datetime.now(UTC).isoformat()
        notification_id = str(uuid4())

        try:
            self._email_sender.send(to_email=student_email, subject=subject, body=message)
            notification = Notification(
                id=notification_id,
                student_email=student_email,
                message=message,
                sent_at=sent_at,
                status="sent",
            )
            return self._repository.save(notification)
        except Exception as exc:
            failed_notification = Notification(
                id=notification_id,
                student_email=student_email,
                message=message,
                sent_at=sent_at,
                status="failed",
            )
            self._repository.save(failed_notification)
            raise EmailSendError("No se pudo enviar el correo de alerta.") from exc
