from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.application.common.unit_of_work import AbstractUnitOfWork
from app.domain.auth.repositories import UserRepository
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
def uow(user_repo, role_repo, label_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.users = user_repo
    mock.roles = role_repo
    mock.labels = label_repo
    return mock
