from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.books.entities import Book, BookStatus
from app.domain.books.repositories import BookRepository
from app.domain.books.value_objects import BookFilePath, BookId, BookTitle
from app.infrastructure.persistence.models.book import BookModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyBookRepository(BookRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, book: Book) -> None:
        model = await self.session.get(BookModel, book.id.value)

        if model is None:
            model = BookModel(
                id=book.id.value,
                title=book.title.value,
                file_path=book.file_path.value,
                status=book.status.value,
                created_at=book.created_at,
            )
            self.session.add(model)
            return

        model.title = book.title.value
        model.file_path = book.file_path.value
        model.status = book.status.value

    async def get(self, book_id: BookId) -> Book | None:
        model = await self.session.get(BookModel, book_id.value)
        if model is None:
            return None

        return Book(
            id=BookId(model.id),
            title=BookTitle(model.title),
            file_path=BookFilePath(model.file_path),
            status=BookStatus(model.status),
            created_at=model.created_at,
        )
