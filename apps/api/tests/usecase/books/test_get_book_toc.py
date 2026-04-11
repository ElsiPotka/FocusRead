from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.books.use_cases.get_book_toc import GetBookTOC
from app.application.common.errors import NotFoundError
from app.application.common.unit_of_work import AbstractUnitOfWork
from app.domain.auth.value_objects import UserId
from app.domain.book_toc_entry.entities import BookTOCEntry
from app.domain.book_toc_entry.repositories import BookTOCEntryRepository
from app.domain.book_toc_entry.value_objects import BookTOCTitle
from app.domain.books.entities import Book
from app.domain.books.repositories import BookRepository
from app.domain.books.value_objects import BookFilePath, BookTitle


@pytest.fixture
def book_repo():
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def toc_repo():
    return AsyncMock(spec=BookTOCEntryRepository)


@pytest.fixture
def uow(book_repo, toc_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.books = book_repo
    mock.book_toc_entries = toc_repo
    return mock


@pytest.fixture
def book() -> Book:
    return Book.create(
        owner_user_id=UserId(uuid4()),
        title=BookTitle("Test Book"),
        file_path=BookFilePath("/tmp/test.pdf"),
    )


async def test_get_book_toc_returns_entries(uow, book_repo, toc_repo, book):
    entries = [
        BookTOCEntry.create(
            book_id=book.id,
            title=BookTOCTitle("Chapter 1"),
            level=1,
            order_index=0,
        ),
        BookTOCEntry.create(
            book_id=book.id,
            title=BookTOCTitle("Chapter 2"),
            level=1,
            order_index=1,
        ),
    ]
    book_repo.get_for_owner.return_value = book
    toc_repo.list_for_book.return_value = entries

    result = await GetBookTOC(uow).execute(
        book_id=book.id.value,
        owner_user_id=book.owner_user_id.value,
    )

    assert len(result) == 2
    assert result[0].title.value == "Chapter 1"
    assert result[1].title.value == "Chapter 2"
    toc_repo.list_for_book.assert_awaited_once()


async def test_get_book_toc_returns_empty_list(uow, book_repo, toc_repo, book):
    book_repo.get_for_owner.return_value = book
    toc_repo.list_for_book.return_value = []

    result = await GetBookTOC(uow).execute(
        book_id=book.id.value,
        owner_user_id=book.owner_user_id.value,
    )

    assert result == []


async def test_get_book_toc_book_not_found(uow, book_repo):
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await GetBookTOC(uow).execute(
            book_id=uuid4(),
            owner_user_id=uuid4(),
        )
