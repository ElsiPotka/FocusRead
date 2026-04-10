from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.shelf.value_objects import (
    ShelfColor,
    ShelfDescription,
    ShelfIcon,
    ShelfId,
    ShelfName,
)

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.shelf.entities import Shelf


class UpdateShelf:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        shelf_id: UUID,
        user_id: UUID,
        name: str | None = None,
        description: str | None = None,
        color: str | None = None,
        icon: str | None = None,
        clear_description: bool = False,
        clear_color: bool = False,
        clear_icon: bool = False,
    ) -> Shelf:
        shelf = await self._uow.shelves.get_for_owner(
            shelf_id=ShelfId(shelf_id),
            user_id=UserId(user_id),
        )
        if shelf is None:
            raise NotFoundError("Shelf not found")

        if name is not None or description is not None or clear_description:
            shelf.rename(
                name=ShelfName(name) if name else shelf.name,
                description=ShelfDescription(description) if description else (None if clear_description else shelf.description),
            )

        if color is not None or icon is not None or clear_color or clear_icon:
            shelf.restyle(
                color=ShelfColor(color) if color else (None if clear_color else shelf.color),
                icon=ShelfIcon(icon) if icon else (None if clear_icon else shelf.icon),
            )

        await self._uow.shelves.save(shelf)
        await self._uow.commit()
        return shelf
