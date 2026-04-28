# src/user_service/app.py
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .application.assign_role_use_case import AssignRoleUseCase
from .application.create_user_use_case import CreateUserUseCase
from .application.get_user_use_case import GetUserUseCase
from .application.update_profile_use_case import UpdateProfileUseCase
from .domain.service.user_domain_service import UserDomainService
from .infrastructure.adapters.inbound.user_router import create_user_router
from .infrastructure.adapters.outbound.postgres_user_repository import PostgresUserRepository
from .infrastructure.config.db_config import build_session_factory


def create_app() -> FastAPI:
    app = FastAPI(title="User Service", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    database_url = os.getenv(
        "USER_DATABASE_URL",
        "postgresql+psycopg2://users_user:users_password@postgres_users:5432/user_db",
    )

    session_factory = build_session_factory(database_url)
    repository = PostgresUserRepository(session_factory)
    user_domain_service = UserDomainService(repository=repository)

    create_user_use_case = CreateUserUseCase(user_domain_service=user_domain_service)
    get_user_use_case = GetUserUseCase(user_domain_service=user_domain_service)
    update_profile_use_case = UpdateProfileUseCase(user_domain_service=user_domain_service)
    assign_role_use_case = AssignRoleUseCase(user_domain_service=user_domain_service)

    app.include_router(
        create_user_router(
            create_user_use_case=create_user_use_case,
            get_user_use_case=get_user_use_case,
            update_profile_use_case=update_profile_use_case,
            assign_role_use_case=assign_role_use_case,
        )
    )

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
