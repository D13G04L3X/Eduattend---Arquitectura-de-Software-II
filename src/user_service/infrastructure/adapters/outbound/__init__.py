# src/user_service/infrastructure/adapters/outbound/__init__.py
from .postgres_user_repository import PostgresUserRepository

__all__ = ["PostgresUserRepository"]
