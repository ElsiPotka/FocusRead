from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.themes import ApplyTheme
from app.domain.theme.entities import Theme
from app.domain.theme.value_objects import ThemeId, ThemeName, ThemeSlug, ThemeTokens

from .conftest import valid_tokens


def _make_theme(owner_user_id=None) -> Theme:
    from app.domain.auth.value_objects import UserId

    return Theme(
        id=ThemeId.generate(),
        name=ThemeName("Test"),
        slug=ThemeSlug("test"),
        tokens=ThemeTokens(valid_tokens()),
        owner_user_id=UserId(owner_user_id) if owner_user_id else None,
    )


class TestApplyTheme:
    @pytest.mark.anyio
    async def test_apply_theme(self, uow, cache, theme_repo):
        uid = uuid4()
        theme = _make_theme()
        theme_repo.get.return_value = theme

        await ApplyTheme(uow, cache).execute(
            user_id=uid,
            theme_id=theme.id.value,
        )

        theme_repo.set_active_theme.assert_awaited_once()
        uow.commit.assert_awaited_once()
        cache.delete.assert_awaited_once()

    @pytest.mark.anyio
    async def test_apply_not_found(self, uow, cache, theme_repo):
        theme_repo.get.return_value = None

        with pytest.raises(NotFoundError):
            await ApplyTheme(uow, cache).execute(
                user_id=uuid4(),
                theme_id=uuid4(),
            )

    @pytest.mark.anyio
    async def test_apply_increments_downloads_for_non_owner(
        self, uow, cache, theme_repo
    ):
        other_owner = uuid4()
        theme = _make_theme(owner_user_id=other_owner)
        theme_repo.get.return_value = theme

        applying_user = uuid4()
        await ApplyTheme(uow, cache).execute(
            user_id=applying_user,
            theme_id=theme.id.value,
        )

        assert theme.download_count == 1
        theme_repo.save.assert_awaited_once()

    @pytest.mark.anyio
    async def test_apply_no_increment_for_owner(self, uow, cache, theme_repo):
        owner = uuid4()
        theme = _make_theme(owner_user_id=owner)
        theme_repo.get.return_value = theme

        await ApplyTheme(uow, cache).execute(
            user_id=owner,
            theme_id=theme.id.value,
        )

        assert theme.download_count == 0
        theme_repo.save.assert_not_awaited()
