# src/user_service/domain/model/user.py
from dataclasses import dataclass
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"
    TEACHER = "teacher"


@dataclass(frozen=True)
class User:
    id: str
    email: str
    full_name: str
    role: UserRole
