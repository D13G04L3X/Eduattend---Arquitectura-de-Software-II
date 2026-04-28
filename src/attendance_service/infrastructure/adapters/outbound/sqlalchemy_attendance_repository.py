from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ....application.ports.outbound.i_attendance_repository import IAttendanceRepository
from ....domain.exception.business_rule_violation import (
    AttendanceNotFoundError,
    DuplicateAttendanceError,
)
from ....domain.model.attendance import Attendance
from ...mappers.attendance_mapper import attendance_from_orm, orm_from_attendance
from .attendance_orm_model import AttendanceOrmModel


class SqlAlchemyAttendanceRepository(IAttendanceRepository):
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def exists_for_student_class_day(
        self,
        student_id: str,
        course_id: str,
        class_session_id: str,
        attendance_date: date,
    ) -> bool:
        session = self._session_factory()
        try:
            statement = select(AttendanceOrmModel.id).where(
                AttendanceOrmModel.student_id == student_id,
                AttendanceOrmModel.course_id == course_id,
                AttendanceOrmModel.class_session_id == class_session_id,
                AttendanceOrmModel.attendance_date == attendance_date,
            )
            return session.execute(statement).first() is not None
        finally:
            session.close()

    def save(self, attendance: Attendance) -> Attendance:
        session = self._session_factory()
        try:
            model = orm_from_attendance(attendance)
            session.add(model)
            session.commit()
            session.refresh(model)
            return attendance_from_orm(model)
        except IntegrityError as exc:
            session.rollback()
            raise DuplicateAttendanceError(
                "El estudiante ya registro asistencia para esta clase en esta fecha."
            ) from exc
        finally:
            session.close()

    def get_by_id(self, attendance_id: int) -> Attendance | None:
        session = self._session_factory()
        try:
            model = session.get(AttendanceOrmModel, attendance_id)
            if model is None:
                return None
            return attendance_from_orm(model)
        finally:
            session.close()

    def update(self, attendance: Attendance) -> Attendance:
        session = self._session_factory()
        try:
            model = session.get(AttendanceOrmModel, attendance.id)
            if model is None:
                raise AttendanceNotFoundError(
                    f"No existe asistencia con id {attendance.id}."
                )

            model.student_id = attendance.student_id
            model.course_id = attendance.course_id
            model.class_session_id = attendance.class_session_id
            model.attendance_date = attendance.attendance_date
            session.commit()
            session.refresh(model)
            return attendance_from_orm(model)
        except IntegrityError as exc:
            session.rollback()
            raise DuplicateAttendanceError(
                "El estudiante ya registro asistencia para esta clase en esta fecha."
            ) from exc
        finally:
            session.close()

    def delete_by_id(self, attendance_id: int) -> bool:
        session = self._session_factory()
        try:
            model = session.get(AttendanceOrmModel, attendance_id)
            if model is None:
                return False
            session.delete(model)
            session.commit()
            return True
        finally:
            session.close()

    def list_all(self) -> list[Attendance]:
        session = self._session_factory()
        try:
            statement = select(AttendanceOrmModel).order_by(AttendanceOrmModel.registered_at.desc())
            rows = session.execute(statement).scalars().all()
            return [attendance_from_orm(row) for row in rows]
        finally:
            session.close()

    def count_by_student_and_course(
        self,
        student_id: str,
        course_id: str,
    ) -> int:
        from sqlalchemy import func
        session = self._session_factory()
        try:
            statement = select(func.count()).where(
                AttendanceOrmModel.student_id == student_id,
                AttendanceOrmModel.course_id == course_id,
            )
            return session.execute(statement).scalar() or 0
        finally:
            session.close()