from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.books.entities import Book
from app.domain.books.value_objects import BookFilePath, BookTitle

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork


class RegisterBookUpload:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def execute(self, *, title: str, file_path: str) -> Book:
        book = Book.create(
            title=BookTitle(title),
            file_path=BookFilePath(file_path),
        )
        await self.uow.books.save(book)
        await self.uow.commit()
        return book
