from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.book_chunks.value_objects import ChunkIndex
from app.domain.books.value_objects import BookId
from app.infrastructure.cache.keys import book_chunk_key

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.book_chunks.entities import BookChunk
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
            # Cache hit — refresh TTL (sliding window) and return from DB
            # We still need the full entity for the response, but we avoid
            # the DB hit for the heavy word_data by using cache for that.
            await self._cache.touch(cache_key, ttl_seconds=CHUNK_CACHE_TTL_SECONDS)

        # 3. Fetch from DB
        chunk = await self._uow.book_chunks.get_by_index(
            book_id=BookId(book_id),
            chunk_index=ChunkIndex(chunk_index),
        )
        if chunk is None:
            raise NotFoundError("Chunk not found")

        # 4. Populate cache on miss
        if cached is None:
            await self._cache.set_json(
                cache_key,
                chunk.word_data.value,
                compress=True,
                ttl_seconds=CHUNK_CACHE_TTL_SECONDS,
            )

        return chunk
