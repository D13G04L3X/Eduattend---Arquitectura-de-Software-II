from typing import Protocol


class IAbsenceEventPublisher(Protocol):
    def publish_absence_limit_reached(
        self,
        student_id: str,
        student_email: str,
        course_id: str,
        absence_count: int,
    ) -> None: ...


class AbsenceEventService:
    def __init__(self, publisher: IAbsenceEventPublisher) -> None:
        self._publisher = publisher

    def check_and_publish(
        self,
        student_id: str,
        student_email: str,
        course_id: str,
        absence_count: int,
        limit: int = 3,
    ) -> None:
        if absence_count == limit:
            self._publisher.publish_absence_limit_reached(
                student_id=student_id,
                student_email=student_email,
                course_id=course_id,
                absence_count=absence_count,
            )
