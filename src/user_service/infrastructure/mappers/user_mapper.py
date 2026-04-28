# src/user_service/infrastructure/mappers/user_mapper.py
from ...domain.model.user import User, UserRole
from ...domain.model.user_profile import UserProfile


def user_from_orm(model) -> User:
    return User(
        id=str(model.id),
        email=model.email,
        full_name=model.full_name,
        role=UserRole(model.role),
    )


def profile_from_orm(model) -> UserProfile:
    return UserProfile(
        user_id=str(model.user_id),
        bio=model.bio,
        avatar_url=model.avatar_url,
        phone=model.phone,
    )
