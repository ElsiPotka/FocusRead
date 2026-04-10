from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.common.unit_of_work import AbstractUnitOfWork
from app.domain.auth.value_objects import UserId
from app.domain.books.entities import Book
from app.domain.books.repositories import BookRepository
from app.domain.books.value_objects import BookFilePath, BookTitle
from app.domain.contributor.repositories import ContributorRepository


@pytest.fixture
def book_repo():
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def contributor_repo():
    return AsyncMock(spec=ContributorRepository)


@pytest.fixture
def uow(book_repo, contributor_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.books = book_repo
    mock.contributors = contributor_repo
    return mock


@pytest.fixture
def book() -> Book:
    return Book.create(
        owner_user_id=UserId(uuid4()),
        title=BookTitle("Test Book"),
        file_path=BookFilePath("/tmp/test.pdf"),
    )
