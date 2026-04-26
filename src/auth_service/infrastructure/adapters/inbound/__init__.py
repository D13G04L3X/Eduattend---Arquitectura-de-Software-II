# src/auth_service/infrastructure/adapters/inbound/__init__.py
from .auth_router import create_auth_router

__all__ = ["create_auth_router"]
