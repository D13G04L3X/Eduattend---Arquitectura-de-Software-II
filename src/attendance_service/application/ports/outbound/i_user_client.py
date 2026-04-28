from typing import Protocol


class IUserClient(Protocol):
    def get_email_by_user_id(self, user_id: str) -> str | None: ...
