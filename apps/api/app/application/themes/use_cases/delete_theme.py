from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.theme.value_objects import ThemeId
from app.infrastructure.cache.keys import theme_key

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.infrastructure.cache.redis_cache import RedisCache


class DeleteTheme:
    def __init__(self, uow: AbstractUnitOfWork, cache: RedisCache) -> None:
        self._uow = uow
        self._cache = cache

    async def execute(
        self,
        *,
        theme_id: UUID,
        user_id: UUID,
        is_admin: bool = False,
    ) -> None:
        if is_admin:
            theme = await self._uow.themes.get(ThemeId(theme_id))
        else:
            theme = await self._uow.themes.get_for_owner(
                theme_id=ThemeId(theme_id),
                user_id=UserId(user_id),
            )
        if theme is None:
            raise NotFoundError("Theme not found")

        theme.guard_not_system()

        await self._uow.themes.delete(ThemeId(theme_id))
        await self._uow.commit()
        await self._cache.delete(theme_key(str(theme_id)))
