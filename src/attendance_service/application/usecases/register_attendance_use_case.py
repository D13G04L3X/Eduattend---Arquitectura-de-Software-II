from datetime import datetime

from ...application.ports.outbound.i_attendance_repository import IAttendanceRepository
from ...application.ports.outbound.i_user_client import IUserClient
from ...domain.exception.business_rule_violation import AbsenceLimitReachedError
from ...domain.model.attendance import Attendance
from ...domain.service.absence_event_service import AbsenceEventService
from ...domain.service.attendance_uniqueness_service import AttendanceUniquenessService
from .register_attendance_command import RegisterAttendanceCommand

ABSENCE_LIMIT = 3


class RegisterAttendanceUseCase:
    def __init__(
        self,
        repository: IAttendanceRepository,
        absence_event_service: AbsenceEventService | None = None,
        user_client: IUserClient | None = None,
    ) -> None:
        self._repository = repository
        self._uniqueness_service = AttendanceUniquenessService(repository)
        self._absence_event_service = absence_event_service
        self._user_client = user_client

    def execute(self, command: RegisterAttendanceCommand) -> Attendance:
        # 1. Verificar que no exista duplicado
        self._uniqueness_service.ensure_attendance_not_registered(
            student_id=command.student_id,
            course_id=command.course_id,
            class_session_id=command.class_session_id,
            attendance_date=command.attendance_date,
        )

        # 2. Verificar que no haya alcanzado el límite ya
        current_count = self._repository.count_by_student_and_course(
            student_id=command.student_id,
            course_id=command.course_id,
        )
        if current_count >= ABSENCE_LIMIT:
            raise AbsenceLimitReachedError(
                f"El estudiante {command.student_id} ya alcanzó el límite de "
                f"{ABSENCE_LIMIT} faltas en el curso {command.course_id}. "
                f"No se pueden registrar más faltas."
            )

        # 3. Guardar la falta
        attendance = Attendance(
            student_id=command.student_id,
            course_id=command.course_id,
            class_session_id=command.class_session_id,
            attendance_date=command.attendance_date,
            registered_at=datetime.utcnow(),
        )
        saved = self._repository.save(attendance)

        # 4. Si con esta falta se alcanza exactamente el límite → notificar
        new_count = current_count + 1
        if self._absence_event_service is not None and new_count == ABSENCE_LIMIT:
            student_email = None
            if self._user_client is not None:
                student_email = self._user_client.get_email_by_user_id(command.student_id)

            if student_email:
                self._absence_event_service.check_and_publish(
                    student_id=command.student_id,
                    student_email=student_email,
                    course_id=command.course_id,
                    absence_count=new_count,
                )

        return saved