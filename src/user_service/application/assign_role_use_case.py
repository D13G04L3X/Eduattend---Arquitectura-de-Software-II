# src/user_service/application/assign_role_use_case.py
from ..domain.model.user import User, UserRole
from ..domain.service.user_domain_service import UserDomainService


class AssignRoleUseCase:
    def __init__(self, user_domain_service: UserDomainService) -> None:
        self._user_domain_service = user_domain_service

    def execute(self, user_id: str, role: str) -> User:
        user_role = UserRole(role)
        return self._user_domain_service.assign_role(user_id=user_id, role=user_role)
