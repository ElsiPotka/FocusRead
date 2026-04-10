from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.common.unit_of_work import AbstractUnitOfWork
from app.domain.auth.value_objects import UserId
from app.domain.books.entities import Book
from app.domain.books.repositories import BookRepository
from app.domain.books.value_objects import BookFilePath, BookTitle
from app.domain.label.entities import Label
from app.domain.label.repositories import LabelRepository
from app.domain.label.value_objects import LabelName, LabelSlug


@pytest.fixture
def book_repo():
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def label_repo():
    return AsyncMock(spec=LabelRepository)


@pytest.fixture
def uow(book_repo, label_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.books = book_repo
    mock.labels = label_repo
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
def label(user_id) -> Label:
    return Label.create(
        name=LabelName("Fiction"),
        slug=LabelSlug("fiction"),
        owner_user_id=user_id,
    )
