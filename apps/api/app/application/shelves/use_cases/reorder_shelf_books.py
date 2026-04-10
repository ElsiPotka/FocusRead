from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.shelf.value_objects import ShelfId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class ReorderShelfBooks:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        shelf_id: UUID,
        user_id: UUID,
        ordering: list[dict[str, object]],
    ) -> list[UUID]:
        shelf = await self._uow.shelves.get_for_owner(
            shelf_id=ShelfId(shelf_id),
            user_id=UserId(user_id),
        )
        if shelf is None:
            raise NotFoundError("Shelf not found")

        parsed = [
            (
                BookId(item["book_id"]),  # type: ignore[arg-type]
                int(item["sort_order"]),  # type: ignore[arg-type]
            )
            for item in ordering
        ]

        await self._uow.shelves.reorder_books(
            shelf_id=shelf.id,
            ordering=parsed,
        )
        await self._uow.commit()
        return await self._uow.shelves.list_book_ids(shelf_id=shelf.id)
