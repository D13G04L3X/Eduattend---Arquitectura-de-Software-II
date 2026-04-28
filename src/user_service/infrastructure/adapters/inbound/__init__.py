# src/user_service/infrastructure/adapters/inbound/__init__.py
from .user_router import create_user_router

__all__ = ["create_user_router"]
