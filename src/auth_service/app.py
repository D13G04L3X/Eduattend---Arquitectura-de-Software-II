# src/auth_service/app.py
import os

from fastapi import FastAPI

from .application.login_use_case import LoginUseCase
from .application.logout_use_case import LogoutUseCase
from .application.refresh_token_use_case import RefreshTokenUseCase
from .domain.service.auth_service import AuthService
from .infrastructure.adapters.inbound.auth_router import create_auth_router
from .infrastructure.adapters.outbound.postgres_user_repository import PostgresUserRepository
from .infrastructure.adapters.outbound.redis_token_store import build_token_store
from .infrastructure.config.db_config import build_session_factory


def create_app() -> FastAPI:
    app = FastAPI(title="Auth Service", version="1.0.0")

    database_url = os.getenv(
        "AUTH_DATABASE_URL",
        "postgresql+psycopg2://auth_user:auth_password@postgres_auth:5432/auth_db",
    )
    jwt_secret = os.getenv("JWT_SECRET", "change-me")
    redis_url = os.getenv("REDIS_URL")

    session_factory = build_session_factory(database_url)
    user_repository = PostgresUserRepository(session_factory)
    token_store = build_token_store(redis_url=redis_url)
    auth_service = AuthService(
        repository=user_repository,
        token_store=token_store,
        jwt_secret=jwt_secret,
    )

    login_use_case = LoginUseCase(auth_service=auth_service)
    refresh_use_case = RefreshTokenUseCase(auth_service=auth_service)
    logout_use_case = LogoutUseCase(auth_service=auth_service)

    app.include_router(
        create_auth_router(
            login_use_case=login_use_case,
            refresh_token_use_case=refresh_use_case,
            logout_use_case=logout_use_case,
        )
    )

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
