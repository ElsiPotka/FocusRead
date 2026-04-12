from __future__ import annotations

import pytest

from app.application.themes import BrowseMarketplace
from app.domain.theme.entities import Theme
from app.domain.theme.value_objects import ThemeId, ThemeName, ThemeSlug, ThemeTokens

from .conftest import valid_tokens


def _make_theme(name: str = "Public Theme") -> Theme:
    return Theme(
        id=ThemeId.generate(),
        name=ThemeName(name),
        slug=ThemeSlug(name.lower().replace(" ", "-")),
        tokens=ThemeTokens(valid_tokens()),
        is_public=True,
    )


class TestBrowseMarketplace:
    @pytest.mark.anyio
    async def test_returns_paginated(self, uow, theme_repo):
        themes = [_make_theme("Theme A"), _make_theme("Theme B")]
        theme_repo.list_public.return_value = (themes, 2)

        result, total = await BrowseMarketplace(uow).execute(
            page=1, per_page=20, sort_by="popular"
        )

        assert len(result) == 2
        assert total == 2
        theme_repo.list_public.assert_awaited_once_with(
            page=1, per_page=20, sort_by="popular", query=None
        )

    @pytest.mark.anyio
    async def test_passes_query(self, uow, theme_repo):
        theme_repo.list_public.return_value = ([], 0)

        await BrowseMarketplace(uow).execute(
            page=1, per_page=10, sort_by="new", query="dark"
        )

        theme_repo.list_public.assert_awaited_once_with(
            page=1, per_page=10, sort_by="new", query="dark"
        )
