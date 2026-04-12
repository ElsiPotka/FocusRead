from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.theme.value_objects import (
    ThemeDescription,
    ThemeId,
    ThemeName,
    ThemeSlug,
    ThemeTokens,
)
from app.infrastructure.cache.keys import theme_key
from app.infrastructure.persistence.models.mixins.slug import SlugMixin

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.theme.entities import Theme
    from app.infrastructure.cache.redis_cache import RedisCache


class UpdateTheme:
    def __init__(self, uow: AbstractUnitOfWork, cache: RedisCache) -> None:
        self._uow = uow
        self._cache = cache

    async def execute(
        self,
        *,
        theme_id: UUID,
        user_id: UUID,
        name: str | None = None,
        description: str | None = None,
        tokens: dict[str, str] | None = None,
        tags: list[str] | None = None,
    ) -> Theme:
        theme = await self._uow.themes.get_for_owner(
            theme_id=ThemeId(theme_id),
            user_id=UserId(user_id),
        )
        if theme is None:
            raise NotFoundError("Theme not found")

        if name is not None:
            theme.rename(
                name=ThemeName(name),
                slug=ThemeSlug(SlugMixin.generate_slug(name)),
                description=ThemeDescription(description) if description else None,
            )
        elif description is not None:
            theme.rename(
                name=theme.name,
                slug=theme.slug,
                description=ThemeDescription(description) if description else None,
            )

        if tokens is not None:
            theme.update_tokens(ThemeTokens(tokens))

        if tags is not None:
            theme.update_tags(tags)

        await self._uow.themes.save(theme)
        await self._uow.commit()
        await self._cache.delete(theme_key(str(theme_id)))
        return theme
