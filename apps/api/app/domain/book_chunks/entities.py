from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.domain.book_chunks.value_objects import (
    BookChunkId,
    ChunkIndex,
    ChunkWordCount,
    ChunkWordData,
    StartWordIndex,
)

if TYPE_CHECKING:
    from app.domain.books.value_objects import BookId


class BookChunk:
    def __init__(
        self,
        *,
        id: BookChunkId,
        book_id: BookId,
        chunk_index: ChunkIndex,
        start_word_index: StartWordIndex,
        word_data: ChunkWordData,
        word_count: ChunkWordCount,
        page_start: int | None = None,
        page_end: int | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        if page_start is not None and page_start <= 0:
            raise ValueError("Page start must be positive.")
        if page_end is not None and page_end <= 0:
            raise ValueError("Page end must be positive.")

        self._id = id
        self._book_id = book_id
        self._chunk_index = chunk_index
        self._start_word_index = start_word_index
        self._word_data = word_data
        self._word_count = word_count
        self._page_start = page_start
        self._page_end = page_end
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        *,
        book_id: BookId,
        chunk_index: ChunkIndex,
        start_word_index: StartWordIndex,
        word_data: ChunkWordData,
        word_count: ChunkWordCount,
        page_start: int | None = None,
        page_end: int | None = None,
    ) -> BookChunk:
        return cls(
            id=BookChunkId.generate(),
            book_id=book_id,
            chunk_index=chunk_index,
            start_word_index=start_word_index,
            word_data=word_data,
            word_count=word_count,
            page_start=page_start,
            page_end=page_end,
        )

    @property
    def id(self) -> BookChunkId:
        return self._id

    @property
    def book_id(self) -> BookId:
        return self._book_id

    @property
    def chunk_index(self) -> ChunkIndex:
        return self._chunk_index

    @property
    def start_word_index(self) -> StartWordIndex:
        return self._start_word_index

    @property
    def word_data(self) -> ChunkWordData:
        return self._word_data

    @property
    def word_count(self) -> ChunkWordCount:
        return self._word_count

    @property
    def page_start(self) -> int | None:
        return self._page_start

    @property
    def page_end(self) -> int | None:
        return self._page_end

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def __eq__(self, other: object) -> bool:
        return isinstance(other, BookChunk) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
