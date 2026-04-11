from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.book_chunks.entities import BookChunk
from app.domain.book_chunks.value_objects import (
    BookChunkId,
    ChunkIndex,
    ChunkWordCount,
    ChunkWordData,
    StartWordIndex,
)
from app.domain.books.value_objects import BookId
from app.infrastructure.cache.keys import book_chunk_key

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.infrastructure.cache.redis_cache import RedisCache

CHUNK_CACHE_TTL_SECONDS = 1800  # 30 minutes


class GetBookChunk:
    def __init__(self, uow: AbstractUnitOfWork, cache: RedisCache) -> None:
        self._uow = uow
        self._cache = cache

    async def execute(
        self,
        *,
        book_id: UUID,
        chunk_index: int,
        owner_user_id: UUID,
    ) -> BookChunk:
        # 1. Verify book ownership
        book = await self._uow.books.get_for_owner(
            book_id=BookId(book_id),
            owner_user_id=UserId(owner_user_id),
        )
        if book is None:
            raise NotFoundError("Book not found")

        # 2. Try Redis cache
        cache_key = book_chunk_key(str(book_id), chunk_index)
        cached = await self._cache.get_json(cache_key)

        if cached is not None:
            # Cache hit — refresh TTL and return without DB query
            await self._cache.touch(cache_key, ttl_seconds=CHUNK_CACHE_TTL_SECONDS)
            return _from_cache(cached)

        # 3. Cache miss — fetch from DB
        chunk = await self._uow.book_chunks.get_by_index(
            book_id=BookId(book_id),
            chunk_index=ChunkIndex(chunk_index),
        )
        if chunk is None:
            raise NotFoundError("Chunk not found")

        # 4. Populate cache with full entity data
        await self._cache.set_json(
            cache_key,
            _to_cache(chunk),
            compress=True,
            ttl_seconds=CHUNK_CACHE_TTL_SECONDS,
        )

        return chunk


def _to_cache(chunk: BookChunk) -> dict[str, Any]:
    return {
        "id": str(chunk.id.value),
        "book_id": str(chunk.book_id.value),
        "chunk_index": chunk.chunk_index.value,
        "start_word_index": chunk.start_word_index.value,
        "word_data": chunk.word_data.value,
        "word_count": chunk.word_count.value,
        "page_start": chunk.page_start,
        "page_end": chunk.page_end,
        "created_at": chunk.created_at.isoformat(),
        "updated_at": chunk.updated_at.isoformat(),
    }


def _from_cache(data: dict[str, Any]) -> BookChunk:
    return BookChunk(
        id=BookChunkId(UUID(data["id"])),
        book_id=BookId(UUID(data["book_id"])),
        chunk_index=ChunkIndex(data["chunk_index"]),
        start_word_index=StartWordIndex(data["start_word_index"]),
        word_data=ChunkWordData(data["word_data"]),
        word_count=ChunkWordCount(data["word_count"]),
        page_start=data.get("page_start"),
        page_end=data.get("page_end"),
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
    )
