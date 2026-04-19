from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.books.use_cases.get_book_chunk import (
    CHUNK_CACHE_TTL_SECONDS,
    GetBookChunk,
    _to_cache,
)
from app.application.common.errors import NotFoundError
from app.application.common.unit_of_work import AbstractUnitOfWork
from app.domain.auth.value_objects import UserId
from app.domain.book_chunks.entities import BookChunk
from app.domain.book_chunks.repositories import BookChunkRepository
from app.domain.book_chunks.value_objects import (
    ChunkIndex,
    ChunkWordCount,
    ChunkWordData,
    StartWordIndex,
)
from app.domain.books.entities import Book
from app.domain.books.repositories import BookRepository
from app.domain.books.value_objects import BookFilePath, BookTitle
from app.infrastructure.cache.redis_cache import RedisCache


@pytest.fixture
def book_repo():
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def chunk_repo():
    return AsyncMock(spec=BookChunkRepository)


@pytest.fixture
def uow(book_repo, chunk_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.books = book_repo
    mock.book_chunks = chunk_repo
    return mock


@pytest.fixture
def cache():
    return AsyncMock(spec=RedisCache)


@pytest.fixture
def book() -> Book:
    return Book.create(
        owner_user_id=UserId(uuid4()),
        title=BookTitle("Test Book"),
        file_path=BookFilePath("/tmp/test.pdf"),
    )


@pytest.fixture
def chunk(book) -> BookChunk:
    return BookChunk.create(
        book_asset_id=book.primary_asset_id,
        chunk_index=ChunkIndex(0),
        start_word_index=StartWordIndex(0),
        word_data=ChunkWordData([["w", "hello", 1.0], ["w", "world", 2.0]]),
        word_count=ChunkWordCount(2),
        page_start=1,
        page_end=1,
    )


async def test_get_chunk_cache_miss_fetches_from_db(
    uow, book_repo, chunk_repo, cache, book, chunk
):
    book_repo.get_for_owner.return_value = book
    cache.get_json.return_value = None
    chunk_repo.get_by_index.return_value = chunk

    result = await GetBookChunk(uow, cache).execute(
        book_id=book.id.value,
        chunk_index=0,
        owner_user_id=book.owner_user_id.value,
    )

    assert result == chunk
    chunk_repo.get_by_index.assert_awaited_once()
    cache.set_json.assert_awaited_once()
    call_kwargs = cache.set_json.call_args.kwargs
    assert call_kwargs["compress"] is True
    assert call_kwargs["ttl_seconds"] == CHUNK_CACHE_TTL_SECONDS


async def test_get_chunk_cache_hit_refreshes_ttl(
    uow, book_repo, chunk_repo, cache, book, chunk
):
    book_repo.get_for_owner.return_value = book
    cache.get_json.return_value = _to_cache(chunk, book_id=book.id)

    result = await GetBookChunk(uow, cache).execute(
        book_id=book.id.value,
        chunk_index=0,
        owner_user_id=book.owner_user_id.value,
    )

    assert result.id.value == chunk.id.value
    assert result.word_data.value == chunk.word_data.value
    chunk_repo.get_by_index.assert_not_awaited()
    cache.touch.assert_awaited_once()
    cache.set_json.assert_not_awaited()


async def test_get_chunk_book_not_found(uow, book_repo, cache):
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await GetBookChunk(uow, cache).execute(
            book_id=uuid4(),
            chunk_index=0,
            owner_user_id=uuid4(),
        )


async def test_get_chunk_chunk_not_found(uow, book_repo, chunk_repo, cache, book):
    book_repo.get_for_owner.return_value = book
    cache.get_json.return_value = None
    chunk_repo.get_by_index.return_value = None

    with pytest.raises(NotFoundError, match="Chunk not found"):
        await GetBookChunk(uow, cache).execute(
            book_id=book.id.value,
            chunk_index=99,
            owner_user_id=book.owner_user_id.value,
        )
