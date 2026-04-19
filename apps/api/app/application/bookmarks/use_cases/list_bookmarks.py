from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.bookmark.entities import Bookmark


class ListBookmarks:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        book_id: UUID,
        user_id: UUID,
    ) -> list[Bookmark]:
        book = await self._uow.books.get_for_owner(
            book_id=BookId(book_id),
            owner_user_id=UserId(user_id),
        )
        if book is None:
            raise NotFoundError("Book not found")
        library_item = await self._uow.library_items.get_active_for_user_book(
            user_id=UserId(user_id),
            book_id=BookId(book_id),
        )
        if library_item is None:
            raise NotFoundError("Library item not found")

        return await self._uow.bookmarks.list_for_library_item(
            library_item_id=library_item.id,
        )
