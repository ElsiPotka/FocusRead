from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.domain.book_toc_entry.entities import BookTOCEntry


class BookTOCEntryResponse(BaseModel):
    id: UUID
    book_id: UUID
    title: str
    level: int
    order_index: int
    parent_id: UUID | None
    page_start: int | None
    start_word_index: int | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_entity(entry: BookTOCEntry) -> BookTOCEntryResponse:
        return BookTOCEntryResponse(
            id=entry.id.value,
            book_id=entry.book_id.value,
            title=entry.title.value,
            level=entry.level,
            order_index=entry.order_index,
            parent_id=entry.parent_id.value if entry.parent_id else None,
            page_start=entry.page_start,
            start_word_index=entry.start_word_index,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
        )
