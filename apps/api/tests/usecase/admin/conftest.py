from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.application.common.unit_of_work import AbstractUnitOfWork
from app.domain.auth.repositories import (
    JWTSigningKeyRepository,
    SessionRepository,
    UserRepository,
)
from app.domain.books.repositories import BookRepository
from app.domain.label.repositories import LabelRepository
from app.domain.role.repositories import RoleRepository


@pytest.fixture
def user_repo():
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def role_repo():
    return AsyncMock(spec=RoleRepository)


@pytest.fixture
def label_repo():
    return AsyncMock(spec=LabelRepository)


@pytest.fixture
def book_repo():
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def session_repo():
    return AsyncMock(spec=SessionRepository)


@pytest.fixture
def jwt_key_repo():
    return AsyncMock(spec=JWTSigningKeyRepository)


@pytest.fixture
def uow(user_repo, role_repo, label_repo, book_repo, session_repo, jwt_key_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.users = user_repo
    mock.roles = role_repo
    mock.labels = label_repo
    mock.books = book_repo
    mock.sessions = session_repo
    mock.jwt_signing_keys = jwt_key_repo
    return mock
