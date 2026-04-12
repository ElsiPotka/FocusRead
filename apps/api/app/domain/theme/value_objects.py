from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import UUID, uuid7

REQUIRED_THEME_KEYS: frozenset[str] = frozenset(
    {
        # Base
        "ink",
        "ink-mid",
        "vellum",
        "vellum-warm",
        # Accent — Burgundy
        "burgundy",
        "burgundy-muted",
        "burgundy-glow",
        # Accent — Verdigris
        "verdigris",
        "verdigris-light",
        # Accent — Gold
        "gold",
        "gold-pale",
        "gold-whisper",
        # Neutrals
        "fog",
        "parchment",
        "ash",
        # Accessibility-adjusted
        "ash-readable",
        "gold-readable",
        # Utility
        "error",
        "error-bg",
        "warning",
        "warning-bg",
        "info",
        "info-bg",
        "success",
        # RSVP
        "rsvp-bg",
        "rsvp-text",
        "rsvp-orp",
        "rsvp-ui",
        "rsvp-ui-bg",
        "rsvp-progress",
        "rsvp-progress-track",
        # Fonts
        "font-display",
        "font-body",
        "font-mono",
        "font-rsvp",
        "font-display-weight",
        "font-body-weight",
        "font-mono-weight",
        "font-rsvp-weight",
        # Layout
        "radius",
        "gap",
    }
)

_DANGEROUS_PATTERNS: re.Pattern[str] = re.compile(
    r"<script|expression\s*\(|javascript:|url\s*\(",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class ThemeId:
    value: UUID

    @classmethod
    def generate(cls) -> ThemeId:
        return cls(value=uuid7())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class ThemeName:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Theme name is required.")
        if len(normalized) > 255:
            raise ValueError("Theme name must be 255 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class ThemeSlug:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not normalized:
            raise ValueError("Theme slug is required.")
        if len(normalized) > 255:
            raise ValueError("Theme slug must be 255 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class ThemeDescription:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Theme description cannot be blank.")
        if len(normalized) > 2000:
            raise ValueError("Theme description must be 2000 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class ThemeTokens:
    value: dict[str, str]

    def __post_init__(self) -> None:
        missing = REQUIRED_THEME_KEYS - self.value.keys()
        if missing:
            raise ValueError(
                f"Theme is missing required tokens: {', '.join(sorted(missing))}"
            )

        for key, val in self.value.items():
            if not isinstance(val, str):
                raise TypeError(f"Token value for '{key}' must be a string.")
            if _DANGEROUS_PATTERNS.search(val):
                raise ValueError(
                    f"Token '{key}' contains a disallowed CSS pattern."
                )
