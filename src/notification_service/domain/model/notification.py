# src/notification_service/domain/model/notification.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Notification:
    id: str
    student_email: str
    message: str
    sent_at: str
    status: str
