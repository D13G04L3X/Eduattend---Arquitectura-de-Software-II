# src/user_service/domain/service/user_domain_service.py
from typing import Protocol
from uuid import uuid4

from ..exception.user_exceptions import DuplicateEmailError, UserNotFoundError
from ..model.user import User, UserRole
from ..model.user_profile import UserProfile


class IUserRepository(Protocol):
    def find_by_id(self, user_id: str) -> User | None: ...

    def find_by_email(self, email: str) -> User | None: ...

    def list_all_users(self) -> list[User]: ...

    def save_user(self, user: User) -> User: ...

    def get_profile(self, user_id: str) -> UserProfile | None: ...

    def save_profile(self, profile: UserProfile) -> UserProfile: ...


class UserDomainService:
    def __init__(self, repository: IUserRepository) -> None:
        self._repository = repository

    def create_user(self, email: str, full_name: str, role: UserRole) -> User:
        self._ensure_email_available(email=email)
        user = User(
            id=str(uuid4()),
            email=email,
            full_name=full_name,
            role=role,
        )
        return self._repository.save_user(user)

    def update_user(self, user_id: str, email: str, full_name: str) -> User:
        existing_user = self._require_user(user_id)
        self._ensure_email_available(email=email, current_user_id=user_id)

        updated_user = User(
            id=existing_user.id,
            email=email,
            full_name=full_name,
            role=existing_user.role,
        )
        return self._repository.save_user(updated_user)

    def get_user(self, user_id: str) -> User:
        return self._require_user(user_id)

    def get_user_with_profile(self, user_id: str) -> tuple[User, UserProfile | None]:
        user = self._require_user(user_id)
        profile = self._repository.get_profile(user_id)
        return user, profile

    def list_users(self) -> list[User]:
        return self._repository.list_all_users()

    def update_profile(
        self,
        user_id: str,
        bio: str | None,
        avatar_url: str | None,
        phone: str | None,
    ) -> UserProfile:
        self._require_user(user_id)
        profile = UserProfile(
            user_id=user_id,
            bio=bio,
            avatar_url=avatar_url,
            phone=phone,
        )
        return self._repository.save_profile(profile)

    def assign_role(self, user_id: str, role: UserRole) -> User:
        user = self._require_user(user_id)
        updated_user = User(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=role,
        )
        return self._repository.save_user(updated_user)

    def _ensure_email_available(
        self,
        email: str,
        current_user_id: str | None = None,
    ) -> None:
        user = self._repository.find_by_email(email)
        if user is None:
            return

        if current_user_id and user.id == current_user_id:
            return

        raise DuplicateEmailError(f"El email {email} ya esta registrado.")

    def _require_user(self, user_id: str) -> User:
        user = self._repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"No existe usuario con id {user_id}.")
        return user
