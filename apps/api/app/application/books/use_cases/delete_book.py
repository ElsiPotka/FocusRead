from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId

if TYPE_CHECKING:
    from uuid import UUID


class DeleteBook:
    def __init__(self, uow) -> None:
        self._uow = uow

    async def execute(self, *, book_id: UUID, owner_user_id: UUID) -> None:
        book = await self._uow.books.get_for_owner(
            book_id=BookId(book_id),
            owner_user_id=UserId(owner_user_id),
        )
        if book is None:
            raise NotFoundError("Book not found")
        await self._uow.books.delete(book_id=book.id)
        await self._uow.commit()
