# src/auth_service/infrastructure/config/__init__.py
from .db_config import Base, build_session_factory

__all__ = ["Base", "build_session_factory"]
