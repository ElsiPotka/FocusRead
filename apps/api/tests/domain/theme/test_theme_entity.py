from __future__ import annotations

from uuid import uuid4

import pytest

from app.domain.auth.value_objects import UserId
from app.domain.theme.entities import Theme, ThemeError
from app.domain.theme.value_objects import (
    REQUIRED_THEME_KEYS,
    ThemeDescription,
    ThemeId,
    ThemeName,
    ThemeSlug,
    ThemeTokens,
)


def _valid_tokens(**overrides: str) -> dict[str, str]:
    base = {key: f"#{i:06x}" for i, key in enumerate(sorted(REQUIRED_THEME_KEYS))}
    base.update(overrides)
    return base


def make_theme(**kwargs) -> Theme:
    defaults: dict = {
        "name": ThemeName("Test Theme"),
        "slug": ThemeSlug("test-theme"),
        "tokens": ThemeTokens(_valid_tokens()),
        "owner_user_id": UserId(uuid4()),
    }
    defaults.update(kwargs)
    return Theme.create(**defaults)


def test_create_defaults():
    theme = make_theme()
    assert theme.name.value == "Test Theme"
    assert theme.slug.value == "test-theme"
    assert theme.is_public is False
    assert theme.is_system is False
    assert theme.is_featured is False
    assert theme.download_count == 0
    assert theme.like_count == 0
    assert theme.forked_from_id is None


def test_create_with_description():
    theme = make_theme(description=ThemeDescription("A test theme"))
    assert theme.description is not None
    assert theme.description.value == "A test theme"


def test_rename():
    theme = make_theme()
    old_updated = theme.updated_at
    theme.rename(
        name=ThemeName("New Name"),
        slug=ThemeSlug("new-name"),
        description=ThemeDescription("New desc"),
    )
    assert theme.name.value == "New Name"
    assert theme.slug.value == "new-name"
    assert theme.description is not None
    assert theme.updated_at >= old_updated


def test_update_tokens():
    theme = make_theme()
    new_tokens = ThemeTokens(_valid_tokens(ink="#ffffff"))
    theme.update_tokens(new_tokens)
    assert theme.tokens.value["ink"] == "#ffffff"


def test_publish_unpublish():
    theme = make_theme()
    assert theme.is_public is False
    theme.publish()
    assert theme.is_public is True
    theme.unpublish()
    assert theme.is_public is False


def test_feature_unfeature():
    theme = make_theme()
    theme.feature()
    assert theme.is_featured is True
    theme.unfeature()
    assert theme.is_featured is False


def test_increment_downloads():
    theme = make_theme()
    theme.increment_downloads()
    assert theme.download_count == 1


def test_increment_decrement_likes():
    theme = make_theme()
    theme.increment_likes()
    theme.increment_likes()
    assert theme.like_count == 2
    theme.decrement_likes()
    assert theme.like_count == 1
    theme.decrement_likes()
    assert theme.like_count == 0
    theme.decrement_likes()  # should not go negative
    assert theme.like_count == 0


def test_guard_not_system_on_user_theme():
    theme = make_theme()
    theme.guard_not_system()  # should not raise


def test_guard_not_system_blocks_system_theme():
    theme = Theme(
        id=ThemeId.generate(),
        name=ThemeName("System"),
        slug=ThemeSlug("system"),
        tokens=ThemeTokens(_valid_tokens()),
        is_system=True,
    )
    with pytest.raises(ThemeError, match="System themes cannot be modified"):
        theme.guard_not_system()


def test_rename_blocked_on_system():
    theme = Theme(
        id=ThemeId.generate(),
        name=ThemeName("System"),
        slug=ThemeSlug("system"),
        tokens=ThemeTokens(_valid_tokens()),
        is_system=True,
    )
    with pytest.raises(ThemeError):
        theme.rename(
            name=ThemeName("Hacked"),
            slug=ThemeSlug("hacked"),
        )


def test_update_tokens_blocked_on_system():
    theme = Theme(
        id=ThemeId.generate(),
        name=ThemeName("System"),
        slug=ThemeSlug("system"),
        tokens=ThemeTokens(_valid_tokens()),
        is_system=True,
    )
    with pytest.raises(ThemeError):
        theme.update_tokens(ThemeTokens(_valid_tokens()))


def test_forked_from_id():
    parent_id = ThemeId.generate()
    theme = make_theme(forked_from_id=parent_id)
    assert theme.forked_from_id == parent_id


def test_equality_by_id():
    theme1 = make_theme()
    theme2 = Theme(
        id=theme1.id,
        name=ThemeName("Different"),
        slug=ThemeSlug("different"),
        tokens=ThemeTokens(_valid_tokens()),
    )
    assert theme1 == theme2


def test_inequality_different_ids():
    assert make_theme() != make_theme()


def test_hash_by_id():
    theme = make_theme()
    assert hash(theme) == hash(ThemeId(theme.id.value))
