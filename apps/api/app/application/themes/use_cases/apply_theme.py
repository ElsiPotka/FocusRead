from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.theme.value_objects import ThemeId
from app.infrastructure.cache.keys import user_active_theme_key

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.infrastructure.cache.redis_cache import RedisCache


class ApplyTheme:
    def __init__(self, uow: AbstractUnitOfWork, cache: RedisCache) -> None:
        self._uow = uow
        self._cache = cache

    async def execute(self, *, user_id: UUID, theme_id: UUID) -> None:
        theme = await self._uow.themes.get(ThemeId(theme_id))
        if theme is None:
            raise NotFoundError("Theme not found")

        # Increment downloads if not the owner
        if theme.owner_user_id is None or theme.owner_user_id.value != user_id:
            theme.increment_downloads()
            await self._uow.themes.save(theme)

        await self._uow.themes.set_active_theme(
            user_id=UserId(user_id),
            theme_id=ThemeId(theme_id),
        )
        await self._uow.commit()

        # Invalidate cached active theme
        await self._cache.delete(user_active_theme_key(str(user_id)))
