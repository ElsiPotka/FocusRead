from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.shelf.value_objects import ShelfId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class RemoveBookFromShelf:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        shelf_id: UUID,
        book_id: UUID,
        user_id: UUID,
    ) -> None:
        shelf = await self._uow.shelves.get_for_owner(
            shelf_id=ShelfId(shelf_id),
            user_id=UserId(user_id),
        )
        if shelf is None:
            raise NotFoundError("Shelf not found")
        library_item = await self._uow.library_items.get_active_for_user_book(
            user_id=UserId(user_id),
            book_id=BookId(book_id),
        )
        if library_item is None:
            raise NotFoundError("Library item not found")

        await self._uow.shelves.remove_library_item(
            shelf_id=shelf.id,
            library_item_id=library_item.id,
        )
        await self._uow.commit()
