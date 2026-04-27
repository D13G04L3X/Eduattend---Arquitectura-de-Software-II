# src/notification_service/infrastructure/adapters/outbound/postgres_notification_repository.py
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ....domain.model.notification import Notification
from ....domain.service.notification_service import INotificationRepository
from ...config.db_config import Base


class NotificationLogOrmModel(Base):
    __tablename__ = "notification_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    student_email: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)


class PostgresNotificationRepository(INotificationRepository):
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def save(self, notification: Notification) -> Notification:
        session = self._session_factory()
        try:
            model = NotificationLogOrmModel(
                id=notification.id,
                student_email=notification.student_email,
                message=notification.message,
                sent_at=datetime.fromisoformat(notification.sent_at),
                status=notification.status,
            )
            session.add(model)
            session.commit()
            return notification
        finally:
            session.close()
