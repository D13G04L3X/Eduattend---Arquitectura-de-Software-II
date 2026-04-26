# src/auth_service/infrastructure/adapters/inbound/auth_router.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from ....application.login_use_case import LoginUseCase
from ....application.logout_use_case import LogoutUseCase
from ....application.refresh_token_use_case import RefreshTokenUseCase
from ....domain.exception.auth_exceptions import InvalidCredentialsError, TokenExpiredError


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


def create_auth_router(
    login_use_case: LoginUseCase,
    refresh_token_use_case: RefreshTokenUseCase,
    logout_use_case: LogoutUseCase,
) -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["auth"])

    @router.post("/login")
    def login(payload: LoginRequest) -> dict[str, str]:
        try:
            return login_use_case.execute(email=payload.email, password=payload.password)
        except InvalidCredentialsError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            ) from exc

    @router.post("/refresh")
    def refresh(payload: RefreshTokenRequest) -> dict[str, str]:
        try:
            return refresh_token_use_case.execute(refresh_token=payload.refresh_token)
        except TokenExpiredError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            ) from exc
        except InvalidCredentialsError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            ) from exc

    @router.post("/logout")
    def logout(payload: LogoutRequest) -> dict[str, str]:
        logout_use_case.execute(refresh_token=payload.refresh_token)
        return {"message": "Sesion finalizada."}

    return router
