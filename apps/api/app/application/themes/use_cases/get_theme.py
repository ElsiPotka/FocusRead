from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.theme.value_objects import ThemeId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.theme.entities import Theme
    from app.infrastructure.cache.redis_cache import RedisCache

THEME_CACHE_TTL_SECONDS = 1800  # 30 minutes


class GetTheme:
    def __init__(self, uow: AbstractUnitOfWork, cache: RedisCache) -> None:
        self._uow = uow
        self._cache = cache

    async def execute(self, *, theme_id: UUID) -> Theme:
        theme = await self._uow.themes.get(ThemeId(theme_id))
        if theme is None:
            raise NotFoundError("Theme not found")
        return theme
