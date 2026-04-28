from abc import ABC, abstractmethod
from datetime import date

from ....domain.model.attendance import Attendance


class IAttendanceRepository(ABC):
    @abstractmethod
    def exists_for_student_class_day(
        self,
        student_id: str,
        course_id: str,
        class_session_id: str,
        attendance_date: date,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def save(self, attendance: Attendance) -> Attendance:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, attendance_id: int) -> Attendance | None:
        raise NotImplementedError

    @abstractmethod
    def update(self, attendance: Attendance) -> Attendance:
        raise NotImplementedError

    @abstractmethod
    def delete_by_id(self, attendance_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Attendance]:
        raise NotImplementedError

    @abstractmethod
    def count_by_student_and_course(
        self,
        student_id: str,
        course_id: str,
    ) -> int:
        raise NotImplementedError