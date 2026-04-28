# src/user_service/application/create_user_use_case.py
from ..domain.model.user import User, UserRole
from ..domain.service.user_domain_service import UserDomainService


class CreateUserUseCase:
    def __init__(self, user_domain_service: UserDomainService) -> None:
        self._user_domain_service = user_domain_service

    def execute(
        self,
        email: str,
        full_name: str,
        role: str = UserRole.STUDENT.value,
        user_id: str | None = None,
    ) -> User:
        user_role = UserRole(role)
        if user_id is None:
            return self._user_domain_service.create_user(
                email=email,
                full_name=full_name,
                role=user_role,
            )

        return self._user_domain_service.update_user(
            user_id=user_id,
            email=email,
            full_name=full_name,
        )
