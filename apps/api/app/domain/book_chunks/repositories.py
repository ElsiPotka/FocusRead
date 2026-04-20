from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.book_asset.value_objects import BookAssetId
    from app.domain.book_chunks.entities import BookChunk
    from app.domain.book_chunks.value_objects import ChunkIndex


class BookChunkRepository(ABC):
    @abstractmethod
    async def save(self, chunk: BookChunk) -> None: ...

    @abstractmethod
    async def save_many(self, chunks: list[BookChunk]) -> None: ...

    @abstractmethod
    async def upsert_by_asset_index(self, chunk: BookChunk) -> BookChunk:
        """Idempotent upsert keyed on (book_asset_id, chunk_index).

        If a chunk already exists at `(chunk.book_asset_id, chunk.chunk_index)`,
        its content is updated in place (reusing the existing primary key so
        the `uq_book_chunks_book_asset_id_chunk_index` constraint resumes
        partial extraction runs safely). Otherwise the incoming chunk is
        inserted. Returns the persisted entity.
        """

    @abstractmethod
    async def get_by_index(
        self, *, book_asset_id: BookAssetId, chunk_index: ChunkIndex
    ) -> BookChunk | None: ...

    @abstractmethod
    async def get_by_word_index(
        self, *, book_asset_id: BookAssetId, start_word_index: int
    ) -> BookChunk | None: ...

    @abstractmethod
    async def count_for_asset(self, *, book_asset_id: BookAssetId) -> int: ...

    @abstractmethod
    async def delete_for_asset(self, *, book_asset_id: BookAssetId) -> None: ...
