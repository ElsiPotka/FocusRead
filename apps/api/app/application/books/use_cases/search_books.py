from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.books.entities import Book
    from app.domain.books.filter import BookFilter


class SearchBooks:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, book_filter: BookFilter) -> list[Book]:
        return await self._uow.books.search(book_filter=book_filter)
