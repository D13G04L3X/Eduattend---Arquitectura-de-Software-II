# src/auth_service/infrastructure/adapters/outbound/redis_token_store.py
import logging

from ....domain.service.auth_service import ITokenStore

LOGGER = logging.getLogger(__name__)
REFRESH_TOKEN_TTL_SECONDS = 7 * 24 * 60 * 60

try:
    import redis
except ImportError:  # pragma: no cover
    redis = None


class RedisTokenStore(ITokenStore):
    def __init__(self, redis_url: str) -> None:
        if redis is None:
            raise RuntimeError("redis no esta instalado.")

        self._client = redis.Redis.from_url(redis_url, decode_responses=True)
        self._client.ping()

    def save(self, token: str, user_id: str) -> None:
        self._client.set(token, user_id, ex=REFRESH_TOKEN_TTL_SECONDS)

    def exists(self, token: str) -> bool:
        return bool(self._client.exists(token))

    def delete(self, token: str) -> None:
        self._client.delete(token)


class InMemoryTokenStore(ITokenStore):
    def __init__(self) -> None:
        self._tokens: dict[str, str] = {}

    def save(self, token: str, user_id: str) -> None:
        self._tokens[token] = user_id

    def exists(self, token: str) -> bool:
        return token in self._tokens

    def delete(self, token: str) -> None:
        self._tokens.pop(token, None)


def build_token_store(redis_url: str | None) -> ITokenStore:
    if not redis_url:
        return InMemoryTokenStore()

    try:
        return RedisTokenStore(redis_url=redis_url)
    except Exception as exc:  # pragma: no cover
        LOGGER.warning(
            "No se pudo usar Redis para refresh tokens. Se usara almacenamiento en memoria. Error: %s",
            exc,
        )
        return InMemoryTokenStore()
