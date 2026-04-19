from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.books.use_cases.resolve_book_chunk import ResolveBookChunk
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
        chunk_index=ChunkIndex(2),
        start_word_index=StartWordIndex(5000),
        word_data=ChunkWordData([["w", "hello", 1.0]]),
        word_count=ChunkWordCount(2500),
        page_start=10,
        page_end=15,
    )


async def test_resolve_returns_correct_chunk_and_offset(
    uow, book_repo, chunk_repo, book, chunk
):
    book_repo.get_for_owner.return_value = book
    chunk_repo.get_by_word_index.return_value = chunk

    result = await ResolveBookChunk(uow).execute(
        book_id=book.id.value,
        word_index=5042,
        owner_user_id=book.owner_user_id.value,
    )

    assert result.chunk_index == 2
    assert result.local_offset == 42
    assert result.start_word_index == 5000
    assert result.word_count == 2500


async def test_resolve_at_chunk_start(uow, book_repo, chunk_repo, book, chunk):
    book_repo.get_for_owner.return_value = book
    chunk_repo.get_by_word_index.return_value = chunk

    result = await ResolveBookChunk(uow).execute(
        book_id=book.id.value,
        word_index=5000,
        owner_user_id=book.owner_user_id.value,
    )

    assert result.local_offset == 0


async def test_resolve_book_not_found(uow, book_repo):
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await ResolveBookChunk(uow).execute(
            book_id=uuid4(),
            word_index=100,
            owner_user_id=uuid4(),
        )


async def test_resolve_word_index_not_found(uow, book_repo, chunk_repo, book):
    book_repo.get_for_owner.return_value = book
    chunk_repo.get_by_word_index.return_value = None

    with pytest.raises(NotFoundError, match="No chunk found"):
        await ResolveBookChunk(uow).execute(
            book_id=book.id.value,
            word_index=999999,
            owner_user_id=book.owner_user_id.value,
        )
