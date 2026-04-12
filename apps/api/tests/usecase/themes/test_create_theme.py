from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.themes import CreateTheme

from .conftest import valid_tokens


class TestCreateTheme:
    @pytest.mark.anyio
    async def test_creates_theme(self, uow, theme_repo):
        user_id = uuid4()
        result = await CreateTheme(uow).execute(
            user_id=user_id,
            name="My Theme",
            tokens=valid_tokens(),
            description="A custom theme",
            tags=["dark", "warm"],
        )

        assert result.name.value == "My Theme"
        assert result.slug.value == "my-theme"
        assert result.owner_user_id is not None
        assert result.owner_user_id.value == user_id
        assert result.is_public is False
        assert result.tags == ["dark", "warm"]
        theme_repo.save.assert_awaited_once()
        uow.commit.assert_awaited_once()

    @pytest.mark.anyio
    async def test_creates_with_forked_from(self, uow, theme_repo):
        parent_id = uuid4()
        result = await CreateTheme(uow).execute(
            user_id=uuid4(),
            name="Fork",
            tokens=valid_tokens(),
            forked_from_id=parent_id,
        )
        assert result.forked_from_id is not None
        assert result.forked_from_id.value == parent_id
