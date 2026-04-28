import json
import urllib.error
import urllib.request

from ....application.ports.outbound.i_user_client import IUserClient


class HttpUserClient(IUserClient):
    def __init__(self, user_service_url: str, timeout_seconds: int = 5) -> None:
        self._base_url = user_service_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def get_email_by_user_id(self, user_id: str) -> str | None:
        url = f"{self._base_url}/users/{user_id}"
        request = urllib.request.Request(url, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                if response.status != 200:
                    return None
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError, ValueError):
            return None

        user = payload.get("user") if isinstance(payload, dict) else None
        email = user.get("email") if isinstance(user, dict) else None
        if not email:
            return None
        return str(email).strip() or None
