from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.application.common.unit_of_work import AbstractUnitOfWork
from app.domain.theme.repositories import ThemeRepository
from app.domain.theme.value_objects import REQUIRED_THEME_KEYS


@pytest.fixture
def theme_repo():
    return AsyncMock(spec=ThemeRepository)


@pytest.fixture
def cache():
    return AsyncMock()


@pytest.fixture
def uow(theme_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.themes = theme_repo
    return mock


def valid_tokens(**overrides: str) -> dict[str, str]:
    base = {key: f"#{i:06x}" for i, key in enumerate(sorted(REQUIRED_THEME_KEYS))}
    base.update(overrides)
    return base
