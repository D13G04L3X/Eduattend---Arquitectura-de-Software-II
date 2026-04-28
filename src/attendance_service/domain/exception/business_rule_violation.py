class BusinessRuleViolation(Exception):
    """Base exception for domain business rules."""


class DuplicateAttendanceError(BusinessRuleViolation):
    """Raised when attendance is registered more than once per class per day."""


class AttendanceNotFoundError(BusinessRuleViolation):
    """Raised when a requested attendance record does not exist."""


class AbsenceLimitReachedError(BusinessRuleViolation):
    """Raised when absence limit is reached for a student/course."""
