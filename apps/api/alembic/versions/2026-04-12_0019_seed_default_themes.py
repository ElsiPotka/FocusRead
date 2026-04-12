"""seed default system themes

Revision ID: 0019
Revises: 0018
Create Date: 2026-04-12
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0019"
down_revision: str | None = "0018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ANTIQUARIAN_TOKENS = {
    # Base
    "ink": "#1A1614",
    "ink-mid": "#2E2824",
    "vellum": "#F5EFE6",
    "vellum-warm": "#EDE5D8",
    # Accent — Burgundy
    "burgundy": "#6B2737",
    "burgundy-muted": "#8C4455",
    "burgundy-glow": "rgba(107,39,55,0.12)",
    # Accent — Verdigris
    "verdigris": "#2D6A5E",
    "verdigris-light": "#4A8C7E",
    # Accent — Gold
    "gold": "#B8912A",
    "gold-pale": "#D4AF6A",
    "gold-whisper": "rgba(184,145,42,0.08)",
    # Neutrals
    "fog": "#C9C1B5",
    "parchment": "#DDD5C8",
    "ash": "#7A7268",
    # Accessibility-adjusted
    "ash-readable": "#9A918A",
    "gold-readable": "#D4AF6A",
    # Utility
    "error": "#C0392B",
    "error-bg": "rgba(192,57,43,0.10)",
    "warning": "#C87F2A",
    "warning-bg": "rgba(200,127,42,0.10)",
    "info": "#3D7A9C",
    "info-bg": "rgba(61,122,156,0.10)",
    "success": "#2D6A5E",
    # RSVP
    "rsvp-bg": "#1C1C1E",
    "rsvp-text": "#E0DDD8",
    "rsvp-orp": "#C0465A",
    "rsvp-ui": "#6B6B6B",
    "rsvp-ui-bg": "#2A2A2C",
    "rsvp-progress": "#6B6B6B",
    "rsvp-progress-track": "#2A2A2C",
    # Fonts
    "font-display": "Cormorant Garamond",
    "font-display-weight": "300",
    "font-body": "Instrument Sans",
    "font-body-weight": "400",
    "font-mono": "DM Mono",
    "font-mono-weight": "300",
    "font-rsvp": "Atkinson Hyperlegible Next",
    "font-rsvp-weight": "500",
    # Layout
    "radius": "2px",
    "gap": "24px",
}

NEUTRAL_FOCUS_TOKENS = {
    # Base — neutral tones (RSVP-inspired)
    "ink": "#1C1C1E",
    "ink-mid": "#2A2A2C",
    "vellum": "#F7F7F7",
    "vellum-warm": "#EFEFEF",
    # Accent — muted variants
    "burgundy": "#C0465A",
    "burgundy-muted": "#9E4A5A",
    "burgundy-glow": "rgba(192,70,90,0.12)",
    "verdigris": "#4A8C7E",
    "verdigris-light": "#6BA89A",
    "gold": "#C4A04A",
    "gold-pale": "#D4B87A",
    "gold-whisper": "rgba(196,160,74,0.08)",
    # Neutrals
    "fog": "#B0B0B0",
    "parchment": "#D8D8D8",
    "ash": "#808080",
    # Accessibility-adjusted
    "ash-readable": "#A0A0A0",
    "gold-readable": "#D4B87A",
    # Utility
    "error": "#C0392B",
    "error-bg": "rgba(192,57,43,0.10)",
    "warning": "#C87F2A",
    "warning-bg": "rgba(200,127,42,0.10)",
    "info": "#3D7A9C",
    "info-bg": "rgba(61,122,156,0.10)",
    "success": "#4A8C7E",
    # RSVP
    "rsvp-bg": "#1C1C1E",
    "rsvp-text": "#E0DDD8",
    "rsvp-orp": "#C0465A",
    "rsvp-ui": "#6B6B6B",
    "rsvp-ui-bg": "#2A2A2C",
    "rsvp-progress": "#6B6B6B",
    "rsvp-progress-track": "#2A2A2C",
    # Fonts — neutral sans throughout
    "font-display": "Atkinson Hyperlegible Next",
    "font-display-weight": "700",
    "font-body": "Atkinson Hyperlegible Next",
    "font-body-weight": "400",
    "font-mono": "DM Mono",
    "font-mono-weight": "300",
    "font-rsvp": "Atkinson Hyperlegible Next",
    "font-rsvp-weight": "500",
    # Layout
    "radius": "4px",
    "gap": "24px",
}

SYSTEM_THEMES = [
    {
        "name": "The Antiquarian Palette",
        "slug": "the-antiquarian-palette",
        "description": "Warm literary tones inspired by rare books, aged paper, and brass library hardware. The default FocusRead theme.",
        "tokens": json.dumps(ANTIQUARIAN_TOKENS),
        "tags": ["dark", "warm", "literary", "default"],
    },
    {
        "name": "Neutral Focus",
        "slug": "neutral-focus",
        "description": "Clinical, distraction-free palette inspired by the RSVP focus mode. Neutral tones maintain cognitive vigilance.",
        "tokens": json.dumps(NEUTRAL_FOCUS_TOKENS),
        "tags": ["dark", "neutral", "minimal", "focus"],
    },
]


def upgrade() -> None:
    for theme in SYSTEM_THEMES:
        op.execute(
            sa.text(
                "INSERT INTO themes "
                "(id, name, slug, description, tokens, tags, is_public, is_system, is_featured, created_at, updated_at) "
                "VALUES (uuidv7(), :name, :slug, :description, CAST(:tokens AS jsonb), :tags, true, true, true, now(), now()) "
                "ON CONFLICT DO NOTHING"
            ).bindparams(
                name=theme["name"],
                slug=theme["slug"],
                description=theme["description"],
                tokens=theme["tokens"],
                tags=theme["tags"],
            )
        )


def downgrade() -> None:
    slugs = [theme["slug"] for theme in SYSTEM_THEMES]
    op.execute(
        sa.text(
            "DELETE FROM themes WHERE is_system = true AND slug = ANY(:slugs)"
        ).bindparams(slugs=slugs)
    )
