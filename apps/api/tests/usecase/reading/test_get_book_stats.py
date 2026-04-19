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
from app.domain.library_item.entities import LibraryItem
from app.domain.library_item.repositories import LibraryItemRepository
from app.domain.library_item.value_objects import LibrarySourceKind
from app.domain.reading_stats.repositories import ReadingStatRepository


@pytest.fixture
def book_repo():
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def stat_repo():
    return AsyncMock(spec=ReadingStatRepository)


@pytest.fixture
def library_item_repo():
    return AsyncMock(spec=LibraryItemRepository)


@pytest.fixture
def uow(book_repo, stat_repo, library_item_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.books = book_repo
    mock.library_items = library_item_repo
    mock.reading_stats = stat_repo
    return mock


@pytest.fixture
def book() -> Book:
    return Book.create(
        owner_user_id=UserId(uuid4()),
        title=BookTitle("Test"),
        file_path=BookFilePath("/tmp/test.pdf"),
    )


@pytest.fixture
def library_item(book: Book) -> LibraryItem:
    return LibraryItem.create(
        user_id=book.owner_user_id,
        book_id=book.id,
        source_kind=LibrarySourceKind.UPLOAD,
    )


async def test_returns_stats_for_owned_book(
    uow, book_repo, stat_repo, library_item_repo, book, library_item
):
    book_repo.get_for_owner.return_value = book
    library_item_repo.get_active_for_user_book.return_value = library_item
    stat_repo.list_for_library_item.return_value = []

    result = await GetBookStats(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
    )

    assert result == []
    stat_repo.list_for_library_item.assert_awaited_once()


async def test_book_not_found_raises(uow, book_repo):
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await GetBookStats(uow).execute(
            book_id=uuid4(),
            user_id=uuid4(),
        )
