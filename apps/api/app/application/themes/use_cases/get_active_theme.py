from __future__ import annotations

from typing import TYPE_CHECKING, TypeGuard

from app.domain.auth.value_objects import UserId
from app.domain.theme.value_objects import ThemeSlug
from app.infrastructure.cache.keys import user_active_theme_key

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.infrastructure.cache.redis_cache import RedisCache
    from app.types import JSONValue

ACTIVE_THEME_CACHE_TTL_SECONDS = 3600  # 1 hour
DEFAULT_THEME_SLUG = "the-antiquarian-palette"


def _is_theme_tokens(value: JSONValue) -> TypeGuard[dict[str, str]]:
    return isinstance(value, dict) and all(
        isinstance(key, str) and isinstance(token, str) for key, token in value.items()
    )


class GetActiveTheme:
    def __init__(self, uow: AbstractUnitOfWork, cache: RedisCache) -> None:
        self._uow = uow
        self._cache = cache

    async def execute(self, *, user_id: UUID) -> dict[str, str]:
        cache_key = user_active_theme_key(str(user_id))
        cached = await self._cache.get_json(cache_key)
        if cached is not None and _is_theme_tokens(cached):
            await self._cache.touch(
                cache_key, ttl_seconds=ACTIVE_THEME_CACHE_TTL_SECONDS
            )
            return cached

        theme_id = await self._uow.themes.get_active_theme_id(
            user_id=UserId(user_id),
        )

        if theme_id is not None:
            theme = await self._uow.themes.get(theme_id)
        else:
            theme = None

        if theme is None:
            theme = await self._uow.themes.get_by_slug(
                slug=ThemeSlug(DEFAULT_THEME_SLUG),
            )

        tokens: dict[str, str] = theme.tokens.value if theme else {}

        await self._cache.set_json(
            cache_key,
            tokens,
            ttl_seconds=ACTIVE_THEME_CACHE_TTL_SECONDS,
        )
        return tokens
