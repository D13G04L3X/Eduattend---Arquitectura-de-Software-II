# src/auth_service/infrastructure/mappers/user_mapper.py
from ...domain.model.user import User


def user_from_orm(model) -> User:
    return User(
        id=str(model.id),
        email=model.email,
        hashed_password=model.hashed_password,
        role=model.role,
    )
