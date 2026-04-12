from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.auth.value_objects import UserId
from app.domain.theme.entities import Theme
from app.domain.theme.value_objects import (
    ThemeDescription,
    ThemeId,
    ThemeName,
    ThemeSlug,
    ThemeTokens,
)
from app.infrastructure.persistence.models.mixins.slug import SlugMixin

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class CreateTheme:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        user_id: UUID,
        name: str,
        tokens: dict[str, str],
        description: str | None = None,
        tags: list[str] | None = None,
        forked_from_id: UUID | None = None,
    ) -> Theme:
        theme = Theme.create(
            name=ThemeName(name),
            slug=ThemeSlug(SlugMixin.generate_slug(name)),
            tokens=ThemeTokens(tokens),
            owner_user_id=UserId(user_id),
            description=ThemeDescription(description) if description else None,
            tags=tags,
            forked_from_id=ThemeId(forked_from_id) if forked_from_id else None,
        )
        await self._uow.themes.save(theme)
        await self._uow.commit()
        return theme
