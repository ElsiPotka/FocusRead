from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from app.domain.auth.value_objects import UserId
from app.domain.shelf.value_objects import ShelfId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.shelf.entities import Shelf


class ShelfOrderingItem(TypedDict):
    shelf_id: UUID
    sort_order: int


class ReorderShelves:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        user_id: UUID,
        ordering: list[ShelfOrderingItem],
    ) -> list[Shelf]:
        parsed = [
            (
                ShelfId(item["shelf_id"]),
                item["sort_order"],
            )
            for item in ordering
        ]

        await self._uow.shelves.reorder_shelves(ordering=parsed)
        await self._uow.commit()
        return await self._uow.shelves.list_for_user(user_id=UserId(user_id))
