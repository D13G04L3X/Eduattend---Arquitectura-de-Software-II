# src/user_service/infrastructure/adapters/inbound/user_router.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from ....application.assign_role_use_case import AssignRoleUseCase
from ....application.create_user_use_case import CreateUserUseCase
from ....application.get_user_use_case import GetUserUseCase
from ....application.update_profile_use_case import UpdateProfileUseCase
from ....domain.exception.user_exceptions import DuplicateEmailError, UserNotFoundError
from ....domain.model.user import User
from ....domain.model.user_profile import UserProfile


class CreateUserRequest(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "student"


class UpdateUserRequest(BaseModel):
    email: EmailStr
    full_name: str


class UpdateProfileRequest(BaseModel):
    bio: str | None = None
    avatar_url: str | None = None
    phone: str | None = None


class AssignRoleRequest(BaseModel):
    role: str


def create_user_router(
    create_user_use_case: CreateUserUseCase,
    get_user_use_case: GetUserUseCase,
    update_profile_use_case: UpdateProfileUseCase,
    assign_role_use_case: AssignRoleUseCase,
) -> APIRouter:
    router = APIRouter(prefix="/users", tags=["users"])

    @router.get("")
    def list_users() -> list[dict]:
        users = get_user_use_case.list_all()
        return [_user_to_dict(user) for user in users]

    @router.post("", status_code=status.HTTP_201_CREATED)
    def create_user(payload: CreateUserRequest) -> dict:
        try:
            user = create_user_use_case.execute(
                email=payload.email,
                full_name=payload.full_name,
                role=payload.role,
            )
            return _user_to_dict(user)
        except DuplicateEmailError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol no valido. Usa admin, student o teacher.",
            ) from exc

    @router.get("/{user_id}")
    def get_user(user_id: str) -> dict:
        try:
            user, profile = get_user_use_case.execute(user_id)
            return {
                "user": _user_to_dict(user),
                "profile": _profile_to_dict(profile),
            }
        except UserNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

    @router.put("/{user_id}")
    def update_user(user_id: str, payload: UpdateUserRequest) -> dict:
        try:
            user = create_user_use_case.execute(
                user_id=user_id,
                email=payload.email,
                full_name=payload.full_name,
            )
            return _user_to_dict(user)
        except UserNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except DuplicateEmailError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc

    @router.put("/{user_id}/profile")
    def update_profile(user_id: str, payload: UpdateProfileRequest) -> dict:
        try:
            profile = update_profile_use_case.execute(
                user_id=user_id,
                bio=payload.bio,
                avatar_url=payload.avatar_url,
                phone=payload.phone,
            )
            return _profile_to_dict(profile)
        except UserNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

    @router.put("/{user_id}/role")
    def assign_role(user_id: str, payload: AssignRoleRequest) -> dict:
        try:
            user = assign_role_use_case.execute(user_id=user_id, role=payload.role)
            return _user_to_dict(user)
        except UserNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol no valido. Usa admin, student o teacher.",
            ) from exc

    return router


def _user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
    }


def _profile_to_dict(profile: UserProfile | None) -> dict | None:
    if profile is None:
        return None

    return {
        "user_id": profile.user_id,
        "bio": profile.bio,
        "avatar_url": profile.avatar_url,
        "phone": profile.phone,
    }
