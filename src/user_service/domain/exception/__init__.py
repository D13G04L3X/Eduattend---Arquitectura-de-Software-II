# src/user_service/domain/exception/__init__.py
from .user_exceptions import DuplicateEmailError, UserNotFoundError

__all__ = ["UserNotFoundError", "DuplicateEmailError"]
