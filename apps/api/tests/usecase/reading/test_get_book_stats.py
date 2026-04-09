from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.common.unit_of_work import AbstractUnitOfWork
from app.application.reading.use_cases.get_book_stats import GetBookStats
from app.domain.auth.value_objects import UserId
from app.domain.books.entities import Book
from app.domain.books.repositories import BookRepository
from app.domain.books.value_objects import BookFilePath, BookTitle
from app.domain.reading_stats.repositories import ReadingStatRepository


@pytest.fixture
def book_repo():
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def stat_repo():
    return AsyncMock(spec=ReadingStatRepository)


@pytest.fixture
def uow(book_repo, stat_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.books = book_repo
    mock.reading_stats = stat_repo
    return mock


@pytest.fixture
def book() -> Book:
    return Book.create(
        owner_user_id=UserId(uuid4()),
        title=BookTitle("Test"),
        file_path=BookFilePath("/tmp/test.pdf"),
    )


async def test_returns_stats_for_owned_book(uow, book_repo, stat_repo, book):
    book_repo.get_for_owner.return_value = book
    stat_repo.list_for_book.return_value = []

    result = await GetBookStats(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
    )

    assert result == []
    stat_repo.list_for_book.assert_awaited_once()


async def test_book_not_found_raises(uow, book_repo):
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await GetBookStats(uow).execute(
            book_id=uuid4(),
            user_id=uuid4(),
        )
