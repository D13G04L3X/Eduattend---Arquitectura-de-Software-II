# src/user_service/domain/model/user_profile.py
from dataclasses import dataclass


@dataclass(frozen=True)
class UserProfile:
    user_id: str
    bio: str | None
    avatar_url: str | None
    phone: str | None
