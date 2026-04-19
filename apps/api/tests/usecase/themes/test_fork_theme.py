from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.themes import ForkTheme
from app.domain.auth.value_objects import UserId
from app.domain.theme.entities import Theme
from app.domain.theme.value_objects import ThemeId, ThemeName, ThemeSlug, ThemeTokens

from .conftest import valid_tokens


def _make_theme(*, is_public: bool = True, is_system: bool = False) -> Theme:
    return Theme(
        id=ThemeId.generate(),
        name=ThemeName("Source Theme"),
        slug=ThemeSlug("source-theme"),
        tokens=ThemeTokens(valid_tokens()),
        owner_user_id=UserId(uuid4()),
        is_public=is_public,
        is_system=is_system,
        tags=["dark", "warm"],
    )


class TestForkTheme:
    @pytest.mark.anyio
    async def test_fork_public_theme(self, uow, theme_repo):
        source = _make_theme()
        theme_repo.get.return_value = source

        uid = uuid4()
        result = await ForkTheme(uow).execute(theme_id=source.id.value, user_id=uid)

        assert result.name.value == "Source Theme (fork)"
        assert result.forked_from_id == source.id
        assert result.owner_user_id is not None
        assert result.owner_user_id.value == uid
        assert result.is_public is False
        assert result.tags == ["dark", "warm"]
        theme_repo.save.assert_awaited_once()
        uow.commit.assert_awaited_once()

    @pytest.mark.anyio
    async def test_fork_system_theme(self, uow, theme_repo):
        source = _make_theme(is_public=True, is_system=True)
        theme_repo.get.return_value = source

        result = await ForkTheme(uow).execute(theme_id=source.id.value, user_id=uuid4())

        assert result.forked_from_id == source.id

    @pytest.mark.anyio
    async def test_fork_private_theme_not_found(self, uow, theme_repo):
        source = _make_theme(is_public=False, is_system=False)
        theme_repo.get.return_value = source

        with pytest.raises(NotFoundError):
            await ForkTheme(uow).execute(theme_id=source.id.value, user_id=uuid4())

    @pytest.mark.anyio
    async def test_fork_nonexistent_theme(self, uow, theme_repo):
        theme_repo.get.return_value = None

        with pytest.raises(NotFoundError):
            await ForkTheme(uow).execute(theme_id=uuid4(), user_id=uuid4())
