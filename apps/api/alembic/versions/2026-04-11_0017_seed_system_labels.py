"""seed system labels

Revision ID: 0017
Revises: 0016
Create Date: 2026-04-11
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0017"
down_revision: str | None = "0016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SYSTEM_LABELS = [
    {"name": "Currently Reading", "slug": "currently-reading", "color": "#3B82F6"},
    {"name": "Want to Read", "slug": "want-to-read", "color": "#8B5CF6"},
    {"name": "Recommended", "slug": "recommended", "color": "#10B981"},
    {"name": "Reference", "slug": "reference", "color": "#F59E0B"},
    {"name": "Textbook", "slug": "textbook", "color": "#6366F1"},
    {"name": "Fiction", "slug": "fiction", "color": "#EC4899"},
    {"name": "Non-Fiction", "slug": "non-fiction", "color": "#14B8A6"},
]


def upgrade() -> None:
    for label in SYSTEM_LABELS:
        op.execute(
            sa.text(
                "INSERT INTO labels (id, name, slug, color, is_system, created_at, updated_at) "
                "VALUES (uuidv7(), :name, :slug, :color, true, now(), now()) "
                "ON CONFLICT DO NOTHING"
            ).bindparams(
                name=label["name"],
                slug=label["slug"],
                color=label["color"],
            )
        )


def downgrade() -> None:
    slugs = [label["slug"] for label in SYSTEM_LABELS]
    op.execute(
        sa.text(
            "DELETE FROM labels WHERE is_system = true AND slug = ANY(:slugs)"
        ).bindparams(slugs=slugs)
    )
