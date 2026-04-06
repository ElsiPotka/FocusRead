from __future__ import annotations

import datetime as dt  # noqa: TC003
import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from app.domain.books.value_objects import BookDocumentType  # noqa: TC001

if TYPE_CHECKING:
    from app.domain.books.entities import Book


class BookResponse(BaseModel):
    id: uuid.UUID
    title: str
    subtitle: str | None
    document_type: str
    description: str | None
    language: str | None
    source_filename: str | None
    cover_image_path: str | None
    publisher: str | None
    published_year: int | None
    page_count: int | None
    word_count: int | None
    total_chunks: int | None
    has_images: bool
    toc_extracted: bool
    status: str
    processing_error: str | None
    created_at: dt.datetime
    updated_at: dt.datetime

    @staticmethod
    def from_entity(book: Book) -> BookResponse:
        return BookResponse(
            id=book.id.value,
            title=book.title.value,
            subtitle=book.subtitle.value if book.subtitle else None,
            document_type=book.document_type.value,
            description=book.description.value if book.description else None,
            language=book.language.value if book.language else None,
            source_filename=(
                book.source_filename.value if book.source_filename else None
            ),
            cover_image_path=(
                book.cover_image_path.value if book.cover_image_path else None
            ),
            publisher=book.publisher.value if book.publisher else None,
            published_year=book.published_year.value if book.published_year else None,
            page_count=book.page_count.value if book.page_count else None,
            word_count=book.word_count.value if book.word_count else None,
            total_chunks=book.total_chunks.value if book.total_chunks else None,
            has_images=book.has_images,
            toc_extracted=book.toc_extracted,
            status=book.status.value,
            processing_error=(
                book.processing_error.value if book.processing_error else None
            ),
            created_at=book.created_at,
            updated_at=book.updated_at,
        )


class UpdateBookRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    subtitle: str | None = Field(default=None, min_length=1, max_length=500)
    document_type: BookDocumentType | None = None
    description: str | None = Field(default=None, min_length=1, max_length=5000)
    language: str | None = Field(default=None, min_length=1, max_length=32)
    source_filename: str | None = Field(default=None, min_length=1, max_length=255)
    cover_image_path: str | None = Field(default=None, min_length=1, max_length=2048)
    publisher: str | None = Field(default=None, min_length=1, max_length=255)
    published_year: int | None = Field(default=None, ge=1, le=9999)
    page_count: int | None = Field(default=None, ge=1)
