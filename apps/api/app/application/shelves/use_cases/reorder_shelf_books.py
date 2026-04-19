from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.shelf.value_objects import ShelfId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.library_item.value_objects import LibraryItemId


class ShelfBookOrderingItem(TypedDict):
    book_id: UUID
    sort_order: int


class ReorderShelfBooks:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        shelf_id: UUID,
        user_id: UUID,
        ordering: list[ShelfBookOrderingItem],
    ) -> list[UUID]:
        shelf = await self._uow.shelves.get_for_owner(
            shelf_id=ShelfId(shelf_id),
            user_id=UserId(user_id),
        )
        if shelf is None:
            raise NotFoundError("Shelf not found")

        parsed = [
            (
                BookId(item["book_id"]),
                item["sort_order"],
            )
            for item in ordering
        ]
        resolved: list[tuple[LibraryItemId, int]] = []
        for book_id, sort_order in parsed:
            library_item = await self._uow.library_items.get_active_for_user_book(
                user_id=UserId(user_id),
                book_id=book_id,
            )
            if library_item is None:
                raise NotFoundError("Library item not found")
            resolved.append((library_item.id, sort_order))

        await self._uow.shelves.reorder_items(
            shelf_id=shelf.id,
            ordering=resolved,
        )
        await self._uow.commit()
        return [
            library_item_id.value
            for library_item_id in await self._uow.shelves.list_library_item_ids(
                shelf_id=shelf.id
            )
        ]
