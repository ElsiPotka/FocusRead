from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.themes import GetActiveTheme
from app.domain.theme.entities import Theme
from app.domain.theme.value_objects import (
    REQUIRED_THEME_KEYS,
    ThemeId,
    ThemeName,
    ThemeSlug,
    ThemeTokens,
)

from .conftest import valid_tokens


def _make_theme(**kwargs) -> Theme:
    tokens = valid_tokens()
    defaults: dict = {
        "id": ThemeId.generate(),
        "name": ThemeName("Default"),
        "slug": ThemeSlug("default"),
        "tokens": ThemeTokens(tokens),
        "is_system": True,
        "is_public": True,
    }
    defaults.update(kwargs)
    return Theme(**defaults)


class TestGetActiveTheme:
    @pytest.mark.anyio
    async def test_cache_hit(self, uow, cache, theme_repo):
        uid = uuid4()
        cached_tokens = {"ink": "#000"}
        cache.get_json.return_value = cached_tokens

        result = await GetActiveTheme(uow, cache).execute(user_id=uid)

        assert result == cached_tokens
        cache.touch.assert_awaited_once()
        theme_repo.get_active_theme_id.assert_not_awaited()

    @pytest.mark.anyio
    async def test_cache_miss_with_active_theme(self, uow, cache, theme_repo):
        uid = uuid4()
        tid = ThemeId.generate()
        theme = _make_theme(id=tid)

        cache.get_json.return_value = None
        theme_repo.get_active_theme_id.return_value = tid
        theme_repo.get.return_value = theme

        result = await GetActiveTheme(uow, cache).execute(user_id=uid)

        assert result == theme.tokens.value
        cache.set_json.assert_awaited_once()

    @pytest.mark.anyio
    async def test_cache_miss_no_active_theme_falls_back_to_default(
        self, uow, cache, theme_repo
    ):
        uid = uuid4()
        default_theme = _make_theme()

        cache.get_json.return_value = None
        theme_repo.get_active_theme_id.return_value = None
        theme_repo.get_by_slug.return_value = default_theme

        result = await GetActiveTheme(uow, cache).execute(user_id=uid)

        assert result == default_theme.tokens.value
        theme_repo.get_by_slug.assert_awaited_once()

    @pytest.mark.anyio
    async def test_cache_miss_no_theme_at_all(self, uow, cache, theme_repo):
        uid = uuid4()
        cache.get_json.return_value = None
        theme_repo.get_active_theme_id.return_value = None
        theme_repo.get_by_slug.return_value = None

        result = await GetActiveTheme(uow, cache).execute(user_id=uid)

        assert result == {}
