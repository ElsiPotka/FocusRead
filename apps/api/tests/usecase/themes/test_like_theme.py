from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.themes import LikeTheme
from app.domain.theme.entities import Theme
from app.domain.theme.value_objects import ThemeId, ThemeName, ThemeSlug, ThemeTokens

from .conftest import valid_tokens


def _make_theme() -> Theme:
    return Theme(
        id=ThemeId.generate(),
        name=ThemeName("Likeable"),
        slug=ThemeSlug("likeable"),
        tokens=ThemeTokens(valid_tokens()),
        is_public=True,
    )


class TestLikeTheme:
    @pytest.mark.anyio
    async def test_like_new(self, uow, theme_repo):
        theme = _make_theme()
        theme_repo.get.return_value = theme
        theme_repo.has_user_liked.return_value = False

        result = await LikeTheme(uow).execute(theme_id=theme.id.value, user_id=uuid4())

        assert result is True
        theme_repo.add_like.assert_awaited_once()
        uow.commit.assert_awaited_once()

    @pytest.mark.anyio
    async def test_unlike(self, uow, theme_repo):
        theme = _make_theme()
        theme_repo.get.return_value = theme
        theme_repo.has_user_liked.return_value = True

        result = await LikeTheme(uow).execute(theme_id=theme.id.value, user_id=uuid4())

        assert result is False
        theme_repo.remove_like.assert_awaited_once()

    @pytest.mark.anyio
    async def test_like_not_found(self, uow, theme_repo):
        theme_repo.get.return_value = None

        with pytest.raises(NotFoundError):
            await LikeTheme(uow).execute(theme_id=uuid4(), user_id=uuid4())
