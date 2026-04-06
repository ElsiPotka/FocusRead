from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.application.common.errors import ApplicationError, NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import (
    BookCoverImagePath,
    BookDescription,
    BookDocumentType,
    BookId,
    BookLanguage,
    BookPageCount,
    BookPublishedYear,
    BookPublisher,
    BookSourceFilename,
    BookSubtitle,
    BookTitle,
)

if TYPE_CHECKING:
    from uuid import UUID


class UpdateBookMetadata:
    def __init__(self, uow) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        book_id: UUID,
        owner_user_id: UUID,
        updates: dict[str, Any],
    ):
        book = await self._uow.books.get_for_owner(
            book_id=BookId(book_id),
            owner_user_id=UserId(owner_user_id),
        )
        if book is None:
            raise NotFoundError("Book not found")

        mapped_updates: dict[str, Any] = {}

        if "title" in updates:
            if updates["title"] is None:
                raise ApplicationError("Title cannot be null")
            mapped_updates["title"] = BookTitle(updates["title"])
        if "subtitle" in updates:
            mapped_updates["subtitle"] = (
                BookSubtitle(updates["subtitle"])
                if updates["subtitle"] is not None
                else None
            )
        if "document_type" in updates:
            if updates["document_type"] is None:
                raise ApplicationError("Document type cannot be null")
            mapped_updates["document_type"] = BookDocumentType(updates["document_type"])
        if "description" in updates:
            mapped_updates["description"] = (
                BookDescription(updates["description"])
                if updates["description"] is not None
                else None
            )
        if "language" in updates:
            mapped_updates["language"] = (
                BookLanguage(updates["language"])
                if updates["language"] is not None
                else None
            )
        if "source_filename" in updates:
            mapped_updates["source_filename"] = (
                BookSourceFilename(updates["source_filename"])
                if updates["source_filename"] is not None
                else None
            )
        if "cover_image_path" in updates:
            mapped_updates["cover_image_path"] = (
                BookCoverImagePath(updates["cover_image_path"])
                if updates["cover_image_path"] is not None
                else None
            )
        if "publisher" in updates:
            mapped_updates["publisher"] = (
                BookPublisher(updates["publisher"])
                if updates["publisher"] is not None
                else None
            )
        if "published_year" in updates:
            mapped_updates["published_year"] = (
                BookPublishedYear(updates["published_year"])
                if updates["published_year"] is not None
                else None
            )
        if "page_count" in updates:
            mapped_updates["page_count"] = (
                BookPageCount(updates["page_count"])
                if updates["page_count"] is not None
                else None
            )

        book.update_metadata(**mapped_updates)
        await self._uow.books.save(book)
        await self._uow.commit()
        return book
