from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.theme.value_objects import ThemeId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class PublishTheme:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, theme_id: UUID, user_id: UUID) -> None:
        theme = await self._uow.themes.get_for_owner(
            theme_id=ThemeId(theme_id),
            user_id=UserId(user_id),
        )
        if theme is None:
            raise NotFoundError("Theme not found")

        theme.publish()
        await self._uow.themes.save(theme)
        await self._uow.commit()


class UnpublishTheme:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, theme_id: UUID, user_id: UUID) -> None:
        theme = await self._uow.themes.get_for_owner(
            theme_id=ThemeId(theme_id),
            user_id=UserId(user_id),
        )
        if theme is None:
            raise NotFoundError("Theme not found")

        theme.unpublish()
        await self._uow.themes.save(theme)
        await self._uow.commit()
