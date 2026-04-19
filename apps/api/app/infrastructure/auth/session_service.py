from __future__ import annotations

import hashlib
import secrets
from typing import TYPE_CHECKING, TypedDict, TypeGuard

from app.infrastructure.cache.keys import build_cache_key
from app.infrastructure.config.settings import settings

if TYPE_CHECKING:
    from app.infrastructure.cache.redis_cache import RedisCache
    from app.types import JSONValue


class SessionCacheEntry(TypedDict):
    session_id: str


class CurrentUserCacheEntry(TypedDict):
    name: str
    surname: str
    email: str
    email_verified: bool
    image: str | None
    is_active: bool


def _is_session_cache_entry(value: JSONValue) -> TypeGuard[SessionCacheEntry]:
    return isinstance(value, dict) and isinstance(value.get("session_id"), str)


def _is_current_user_cache_entry(
    value: JSONValue,
) -> TypeGuard[CurrentUserCacheEntry]:
    return (
        isinstance(value, dict)
        and isinstance(value.get("name"), str)
        and isinstance(value.get("surname"), str)
        and isinstance(value.get("email"), str)
        and isinstance(value.get("email_verified"), bool)
        and (value.get("image") is None or isinstance(value.get("image"), str))
        and isinstance(value.get("is_active"), bool)
    )


class SessionService:
    def __init__(self, cache: RedisCache) -> None:
        self._cache = cache

    @staticmethod
    def generate_refresh_token() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(raw: str) -> str:
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    async def cache_session(
        self, token_hash: str, session_id: str, ttl: int | None = None
    ) -> None:
        key = build_cache_key("auth", "session", token_hash)
        await self._cache.set_json(
            key,
            {"session_id": session_id},
            ttl_seconds=ttl or settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        )

    async def get_cached_session(self, token_hash: str) -> SessionCacheEntry | None:
        key = build_cache_key("auth", "session", token_hash)
        cached = await self._cache.get_json(key)
        if cached is None or not _is_session_cache_entry(cached):
            return None
        return cached

    async def invalidate_cached_session(self, token_hash: str) -> None:
        key = build_cache_key("auth", "session", token_hash)
        await self._cache.delete(key)

    async def cache_current_user(
        self, user_id: str, data: CurrentUserCacheEntry, ttl: int = 300
    ) -> None:
        key = build_cache_key("auth", "user", user_id)
        await self._cache.set_json(key, data, ttl_seconds=ttl)

    async def get_cached_current_user(
        self, user_id: str
    ) -> CurrentUserCacheEntry | None:
        key = build_cache_key("auth", "user", user_id)
        cached = await self._cache.get_json(key)
        if cached is None or not _is_current_user_cache_entry(cached):
            return None
        return cached

    async def invalidate_current_user(self, user_id: str) -> None:
        key = build_cache_key("auth", "user", user_id)
        await self._cache.delete(key)
