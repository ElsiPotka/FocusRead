from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.auth.value_objects import UserId
from app.domain.shelf.value_objects import ShelfId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.shelf.entities import Shelf


class ReorderShelves:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        user_id: UUID,
        ordering: list[dict[str, object]],
    ) -> list[Shelf]:
        parsed = [
            (
                ShelfId(item["shelf_id"]),  # type: ignore[arg-type]
                int(item["sort_order"]),  # type: ignore[arg-type]
            )
            for item in ordering
        ]

        await self._uow.shelves.reorder_shelves(ordering=parsed)
        await self._uow.commit()
        return await self._uow.shelves.list_for_user(user_id=UserId(user_id))
