from __future__ import annotations

import pytest

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


# ── ThemeId ──


def test_theme_id_generate():
    tid = ThemeId.generate()
    assert tid.value is not None
    assert str(tid) == str(tid.value)


# ── ThemeName ──


def test_theme_name_strips_whitespace():
    assert ThemeName("  My Theme  ").value == "My Theme"


def test_theme_name_empty_raises():
    with pytest.raises(ValueError, match="required"):
        ThemeName("   ")


def test_theme_name_too_long():
    with pytest.raises(ValueError, match="255"):
        ThemeName("x" * 256)


# ── ThemeSlug ──


def test_theme_slug_lowercase():
    assert ThemeSlug("My-Theme").value == "my-theme"


def test_theme_slug_empty_raises():
    with pytest.raises(ValueError, match="required"):
        ThemeSlug("")


# ── ThemeDescription ──


def test_theme_description_strips():
    assert ThemeDescription("  desc  ").value == "desc"


def test_theme_description_blank_raises():
    with pytest.raises(ValueError, match="blank"):
        ThemeDescription("  ")


def test_theme_description_too_long():
    with pytest.raises(ValueError, match="2000"):
        ThemeDescription("x" * 2001)


# ── ThemeTokens ──


def test_theme_tokens_valid():
    tokens = ThemeTokens(_valid_tokens())
    assert isinstance(tokens.value, dict)
    assert len(tokens.value) >= len(REQUIRED_THEME_KEYS)


def test_theme_tokens_missing_keys():
    incomplete = {"ink": "#000"}
    with pytest.raises(ValueError, match="missing required tokens"):
        ThemeTokens(incomplete)


def test_theme_tokens_extra_keys_allowed():
    t = _valid_tokens(**{"custom-token": "#abc"})
    tokens = ThemeTokens(t)
    assert "custom-token" in tokens.value


def test_theme_tokens_rejects_script():
    t = _valid_tokens(ink="<script>alert(1)</script>")
    with pytest.raises(ValueError, match="disallowed CSS pattern"):
        ThemeTokens(t)


def test_theme_tokens_rejects_expression():
    t = _valid_tokens(ink="expression(alert(1))")
    with pytest.raises(ValueError, match="disallowed CSS pattern"):
        ThemeTokens(t)


def test_theme_tokens_rejects_javascript():
    t = _valid_tokens(ink="javascript:void(0)")
    with pytest.raises(ValueError, match="disallowed CSS pattern"):
        ThemeTokens(t)


def test_theme_tokens_rejects_url():
    t = _valid_tokens(ink="url(http://evil.com)")
    with pytest.raises(ValueError, match="disallowed CSS pattern"):
        ThemeTokens(t)


def test_theme_tokens_non_string_value():
    t = _valid_tokens()
    t["ink"] = 123  # type: ignore[assignment]
    with pytest.raises(TypeError, match="must be a string"):
        ThemeTokens(t)
