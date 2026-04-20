from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, TypedDict, TypeGuard
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
from app.infrastructure.cache.keys import book_asset_chunk_key

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.book_asset.value_objects import BookAssetId
    from app.infrastructure.cache.redis_cache import RedisCache
    from app.types import JSONValue

CHUNK_CACHE_TTL_SECONDS = 1800  # 30 minutes


class CachedBookChunk(TypedDict):
    id: str
    book_id: str
    chunk_index: int
    start_word_index: int
    word_data: list[list[object]]
    word_count: int
    page_start: int | None
    page_end: int | None
    created_at: str
    updated_at: str


def _is_cached_book_chunk(value: JSONValue) -> TypeGuard[CachedBookChunk]:
    return (
        isinstance(value, dict)
        and isinstance(value.get("id"), str)
        and isinstance(value.get("book_id"), str)
        and isinstance(value.get("chunk_index"), int)
        and isinstance(value.get("start_word_index"), int)
        and isinstance(value.get("word_data"), list)
        and isinstance(value.get("word_count"), int)
        and (
            value.get("page_start") is None or isinstance(value.get("page_start"), int)
        )
        and (value.get("page_end") is None or isinstance(value.get("page_end"), int))
        and isinstance(value.get("created_at"), str)
        and isinstance(value.get("updated_at"), str)
    )


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
        book = await self._uow.books.get_for_owner(
            book_id=BookId(book_id),
            owner_user_id=UserId(owner_user_id),
        )
        if book is None:
            raise NotFoundError("Book not found")

        cache_key = book_asset_chunk_key(str(book.primary_asset_id.value), chunk_index)
        cached = await self._cache.get_json(cache_key)

        if cached is not None and _is_cached_book_chunk(cached):
            await self._cache.touch(cache_key, ttl_seconds=CHUNK_CACHE_TTL_SECONDS)
            return _from_cache(cached, book_asset_id=book.primary_asset_id)

        chunk = await self._uow.book_chunks.get_by_index(
            book_asset_id=book.primary_asset_id,
            chunk_index=ChunkIndex(chunk_index),
        )
        if chunk is None:
            raise NotFoundError("Chunk not found")

        await self._cache.set_json(
            cache_key,
            _to_cache(chunk, book_id=book.id),
            compress=True,
            ttl_seconds=CHUNK_CACHE_TTL_SECONDS,
        )

        return chunk


def _to_cache(chunk: BookChunk, *, book_id: BookId) -> CachedBookChunk:
    return {
        "id": str(chunk.id.value),
        "book_id": str(book_id.value),
        "chunk_index": chunk.chunk_index.value,
        "start_word_index": chunk.start_word_index.value,
        "word_data": chunk.word_data.value,
        "word_count": chunk.word_count.value,
        "page_start": chunk.page_start,
        "page_end": chunk.page_end,
        "created_at": chunk.created_at.isoformat(),
        "updated_at": chunk.updated_at.isoformat(),
    }


def _from_cache(data: CachedBookChunk, *, book_asset_id: BookAssetId) -> BookChunk:
    return BookChunk(
        id=BookChunkId(UUID(data["id"])),
        book_asset_id=book_asset_id,
        chunk_index=ChunkIndex(data["chunk_index"]),
        start_word_index=StartWordIndex(data["start_word_index"]),
        word_data=ChunkWordData(data["word_data"]),
        word_count=ChunkWordCount(data["word_count"]),
        page_start=data.get("page_start"),
        page_end=data.get("page_end"),
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
    )
