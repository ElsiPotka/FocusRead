from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
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


class ForkTheme:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        theme_id: UUID,
        user_id: UUID,
    ) -> Theme:
        source = await self._uow.themes.get(ThemeId(theme_id))
        if source is None or (not source.is_public and not source.is_system):
            raise NotFoundError("Theme not found")

        fork_name = f"{source.name.value} (fork)"
        forked = Theme.create(
            name=ThemeName(fork_name),
            slug=ThemeSlug(SlugMixin.generate_slug(fork_name)),
            tokens=ThemeTokens(dict(source.tokens.value)),
            owner_user_id=UserId(user_id),
            description=ThemeDescription(source.description.value) if source.description else None,
            tags=list(source.tags) if source.tags else None,
            forked_from_id=source.id,
        )
        await self._uow.themes.save(forked)
        await self._uow.commit()
        return forked
