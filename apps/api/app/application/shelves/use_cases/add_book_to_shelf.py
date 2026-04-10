from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.shelf.value_objects import ShelfId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class AddBookToShelf:
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

        book = await self._uow.books.get_for_owner(
            book_id=BookId(book_id),
            owner_user_id=UserId(user_id),
        )
        if book is None:
            raise NotFoundError("Book not found")

        current_ids = await self._uow.shelves.list_book_ids(shelf_id=shelf.id)
        next_order = len(current_ids)

        await self._uow.shelves.add_book(
            shelf_id=shelf.id,
            book_id=book.id,
            sort_order=next_order,
        )
        await self._uow.commit()
