from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.common.unit_of_work import AbstractUnitOfWork
from app.domain.auth.value_objects import UserId
from app.domain.books.entities import Book
from app.domain.books.repositories import BookRepository
from app.domain.books.value_objects import BookFilePath, BookTitle
from app.domain.library_item.entities import LibraryItem
from app.domain.library_item.repositories import LibraryItemRepository
from app.domain.library_item.value_objects import LibrarySourceKind
from app.domain.shelf.entities import Shelf
from app.domain.shelf.repositories import ShelfRepository
from app.domain.shelf.value_objects import ShelfName


@pytest.fixture
def book_repo():
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def shelf_repo():
    return AsyncMock(spec=ShelfRepository)


@pytest.fixture
def library_item_repo():
    return AsyncMock(spec=LibraryItemRepository)


@pytest.fixture
def uow(book_repo, shelf_repo, library_item_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.books = book_repo
    mock.library_items = library_item_repo
    mock.shelves = shelf_repo
    return mock


@pytest.fixture
def user_id() -> UserId:
    return UserId(uuid4())


@pytest.fixture
def book(user_id) -> Book:
    return Book.create(
        owner_user_id=user_id,
        title=BookTitle("Test Book"),
        file_path=BookFilePath("/tmp/test.pdf"),
    )


@pytest.fixture
def shelf(user_id) -> Shelf:
    return Shelf.create(
        user_id=user_id,
        name=ShelfName("Test Shelf"),
    )


@pytest.fixture
def library_item(user_id: UserId, book: Book) -> LibraryItem:
    return LibraryItem.create(
        user_id=user_id,
        book_id=book.id,
        source_kind=LibrarySourceKind.UPLOAD,
    )
