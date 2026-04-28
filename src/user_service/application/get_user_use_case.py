# src/user_service/application/get_user_use_case.py
from ..domain.model.user import User
from ..domain.model.user_profile import UserProfile
from ..domain.service.user_domain_service import UserDomainService


class GetUserUseCase:
    def __init__(self, user_domain_service: UserDomainService) -> None:
        self._user_domain_service = user_domain_service

    def execute(self, user_id: str) -> tuple[User, UserProfile | None]:
        return self._user_domain_service.get_user_with_profile(user_id=user_id)

    def list_all(self) -> list[User]:
        return self._user_domain_service.list_users()
