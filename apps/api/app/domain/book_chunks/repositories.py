from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.book_chunks.entities import BookChunk
    from app.domain.book_chunks.value_objects import ChunkIndex
    from app.domain.books.value_objects import BookId


class BookChunkRepository(ABC):
    @abstractmethod
    async def save(self, chunk: BookChunk) -> None: ...

    @abstractmethod
    async def save_many(self, chunks: list[BookChunk]) -> None: ...

    @abstractmethod
    async def get_by_index(
        self, *, book_id: BookId, chunk_index: ChunkIndex
    ) -> BookChunk | None: ...

    @abstractmethod
    async def get_by_word_index(
        self, *, book_id: BookId, start_word_index: int
    ) -> BookChunk | None: ...

    @abstractmethod
    async def count_for_book(self, *, book_id: BookId) -> int: ...

    @abstractmethod
    async def delete_for_book(self, *, book_id: BookId) -> None: ...
