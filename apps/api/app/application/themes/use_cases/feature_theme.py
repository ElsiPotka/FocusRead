from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.theme.value_objects import ThemeId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class FeatureTheme:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, theme_id: UUID) -> None:
        theme = await self._uow.themes.get(ThemeId(theme_id))
        if theme is None:
            raise NotFoundError("Theme not found")

        theme.feature()
        await self._uow.themes.save(theme)
        await self._uow.commit()


class UnfeatureTheme:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, theme_id: UUID) -> None:
        theme = await self._uow.themes.get(ThemeId(theme_id))
        if theme is None:
            raise NotFoundError("Theme not found")

        theme.unfeature()
        await self._uow.themes.save(theme)
        await self._uow.commit()
