# src/notification_service/application/send_absence_alert_use_case.py
from ..domain.model.notification import Notification
from ..domain.service.notification_service import NotificationService


class SendAbsenceAlertUseCase:
    def __init__(self, notification_service: NotificationService) -> None:
        self._notification_service = notification_service

    def execute(self, absence_event: dict) -> Notification:
        student_email = str(absence_event.get("student_email", "")).strip()
        if not student_email:
            raise ValueError("El evento no contiene student_email.")

        student_name = str(
            absence_event.get("student_name")
            or absence_event.get("student_id")
            or "Estudiante"
        )
        course_id = str(absence_event.get("course_id", "N/A"))
        absence_count = int(absence_event.get("count", 0))

        subject = "⚠️ Límite de faltas alcanzado"
        message = (
            f"Hola {student_name},\n\n"
            f"Has alcanzado el limite de faltas en el curso {course_id}.\n"
            f"Cantidad actual de faltas: {absence_count}.\n\n"
            "Por favor contacta a tu docente para regularizar tu situacion."
        )

        return self._notification_service.send_notification(
            student_email=student_email,
            subject=subject,
            message=message,
        )
