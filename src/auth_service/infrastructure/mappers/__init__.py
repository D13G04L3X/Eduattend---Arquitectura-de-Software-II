# src/auth_service/infrastructure/mappers/__init__.py
from .user_mapper import user_from_orm

__all__ = ["user_from_orm"]
