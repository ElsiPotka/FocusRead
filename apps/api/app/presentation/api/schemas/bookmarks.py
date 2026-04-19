from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.domain.bookmark.entities import Bookmark


class BookmarkResponse(BaseModel):
    id: UUID
    user_id: UUID
    book_id: UUID
    word_index: int
    chunk_index: int | None
    page_number: int | None
    label: str | None
    note: str | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_entity(
        bookmark: Bookmark,
        *,
        user_id: UUID,
        book_id: UUID,
    ) -> BookmarkResponse:
        return BookmarkResponse(
            id=bookmark.id.value,
            user_id=user_id,
            book_id=book_id,
            word_index=bookmark.word_index,
            chunk_index=bookmark.chunk_index,
            page_number=bookmark.page_number,
            label=bookmark.label.value if bookmark.label else None,
            note=bookmark.note.value if bookmark.note else None,
            created_at=bookmark.created_at,
            updated_at=bookmark.updated_at,
        )


class CreateBookmarkRequest(BaseModel):
    word_index: int = Field(..., ge=0)
    chunk_index: int | None = Field(default=None, ge=0)
    page_number: int | None = Field(default=None, gt=0)
    label: str | None = Field(default=None, min_length=1, max_length=255)
    note: str | None = Field(default=None, min_length=1, max_length=5000)


class UpdateBookmarkRequest(BaseModel):
    word_index: int | None = Field(default=None, ge=0)
    chunk_index: int | None = Field(default=None, ge=0)
    page_number: int | None = Field(default=None, gt=0)
    label: str | None = Field(default=None, min_length=1, max_length=255)
    note: str | None = Field(default=None, min_length=1, max_length=5000)
    clear_label: bool = False
    clear_note: bool = False
