from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.auth.value_objects import UserId
from app.domain.books.entities import Book
from app.domain.books.value_objects import (
    BookDocumentType,
    BookFilePath,
    BookSourceFilename,
    BookTitle,
)

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class RegisterBookUpload:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self,
        *,
        owner_user_id: UUID,
        title: str,
        file_path: str,
        source_filename: str | None = None,
        document_type: str = BookDocumentType.BOOK.value,
    ) -> Book:
        book = Book.create(
            owner_user_id=UserId(owner_user_id),
            title=BookTitle(title),
            file_path=BookFilePath(file_path),
            source_filename=(
                BookSourceFilename(source_filename) if source_filename else None
            ),
            document_type=BookDocumentType(document_type),
        )
        await self.uow.books.save(book)
        await self.uow.commit()
        return book
