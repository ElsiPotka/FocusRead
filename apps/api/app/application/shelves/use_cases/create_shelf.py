from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.auth.value_objects import UserId
from app.domain.shelf.entities import Shelf
from app.domain.shelf.value_objects import (
    ShelfColor,
    ShelfDescription,
    ShelfIcon,
    ShelfName,
)

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class CreateShelf:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        user_id: UUID,
        name: str,
        description: str | None = None,
        color: str | None = None,
        icon: str | None = None,
    ) -> Shelf:
        shelf = Shelf.create(
            user_id=UserId(user_id),
            name=ShelfName(name),
            description=ShelfDescription(description) if description else None,
            color=ShelfColor(color) if color else None,
            icon=ShelfIcon(icon) if icon else None,
        )
        await self._uow.shelves.save(shelf)
        await self._uow.commit()
        return shelf
