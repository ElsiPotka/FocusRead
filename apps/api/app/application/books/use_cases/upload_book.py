from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, cast

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
    from app.infrastructure.storage.file_storage import FileStorage


class _BookProcessingTask(Protocol):
    def delay(self, book_id: str) -> object: ...


class UploadBook:
    def __init__(self, uow: AbstractUnitOfWork, file_storage: FileStorage) -> None:
        self._uow = uow
        self._file_storage = file_storage

    async def execute(
        self,
        *,
        owner_user_id: UUID,
        title: str,
        source_filename: str,
        file_content: bytes,
        document_type: str = BookDocumentType.BOOK.value,
    ) -> Book:
        book = Book.create(
            owner_user_id=UserId(owner_user_id),
            title=BookTitle(title),
            file_path=BookFilePath("pending"),
            source_filename=(
                BookSourceFilename(source_filename) if source_filename else None
            ),
            document_type=BookDocumentType(document_type),
        )

        storage_destination = f"{owner_user_id}/{book.id.value}/{source_filename}"
        saved_path = await self._file_storage.save_upload(
            file_content=file_content,
            destination=storage_destination,
        )

        book._file_path = BookFilePath(saved_path)

        await self._uow.books.save(book)
        await self._uow.commit()

        from app.workers.task import process_book_task

        cast("_BookProcessingTask", process_book_task).delay(str(book.id.value))

        return book
