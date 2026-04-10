from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.shelf.value_objects import ShelfId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.shelf.entities import Shelf


class GetShelf:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, shelf_id: UUID, user_id: UUID) -> Shelf:
        shelf = await self._uow.shelves.get_for_owner(
            shelf_id=ShelfId(shelf_id),
            user_id=UserId(user_id),
        )
        if shelf is None:
            raise NotFoundError("Shelf not found")
        return shelf
