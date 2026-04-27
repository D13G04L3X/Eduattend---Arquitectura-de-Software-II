# src/notification_service/domain/service/__init__.py
from .notification_service import IEmailSender, INotificationRepository, NotificationService

__all__ = ["IEmailSender", "INotificationRepository", "NotificationService"]
