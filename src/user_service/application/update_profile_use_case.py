# src/user_service/application/update_profile_use_case.py
from ..domain.model.user_profile import UserProfile
from ..domain.service.user_domain_service import UserDomainService


class UpdateProfileUseCase:
    def __init__(self, user_domain_service: UserDomainService) -> None:
        self._user_domain_service = user_domain_service

    def execute(
        self,
        user_id: str,
        bio: str | None,
        avatar_url: str | None,
        phone: str | None,
    ) -> UserProfile:
        return self._user_domain_service.update_profile(
            user_id=user_id,
            bio=bio,
            avatar_url=avatar_url,
            phone=phone,
        )
