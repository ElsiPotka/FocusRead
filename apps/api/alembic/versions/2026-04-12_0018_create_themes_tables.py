"""create themes, user_active_themes, and theme_likes tables

Revision ID: 0018
Revises: 0017
Create Date: 2026-04-12
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from alembic import op
from app.infrastructure.persistence.migrations.search import (
    create_search_vector_index,
    drop_search_vector_index,
    search_vector_column,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0018"
down_revision: str | None = "0017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "themes",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("owner_user_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "slug",
            sa.String(length=255),
            nullable=False,
            comment="URL-friendly identifier",
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tokens", JSONB(), nullable=False),
        sa.Column("preview_image_url", sa.String(length=512), nullable=True),
        sa.Column("tags", ARRAY(sa.String()), nullable=True, comment="Array of tags"),
        sa.Column(
            "is_public",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "is_system",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "is_featured",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "download_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "like_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("forked_from_id", sa.UUID(), nullable=True),
        sa.Column(
            "version",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        search_vector_column(
            searchable_columns=("name", "slug"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_themes_owner_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["forked_from_id"],
            ["themes.id"],
            name=op.f("fk_themes_forked_from_id_themes"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_themes")),
    )

    op.create_index("ix_themes_slug", "themes", ["slug"], unique=True)
    op.create_index("ix_themes_owner", "themes", ["owner_user_id"])
    op.create_index(
        "ix_themes_public_popular",
        "themes",
        ["is_public", sa.text("download_count DESC")],
        postgresql_where=sa.text("is_public = true"),
    )
    op.create_index(
        "ix_themes_public_new",
        "themes",
        ["is_public", sa.text("created_at DESC")],
        postgresql_where=sa.text("is_public = true"),
    )
    create_search_vector_index(op, table_name="themes")

    op.create_table(
        "user_active_themes",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("theme_id", sa.UUID(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_active_themes_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["theme_id"],
            ["themes.id"],
            name=op.f("fk_user_active_themes_theme_id_themes"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_user_active_themes")),
    )

    op.create_table(
        "theme_likes",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("theme_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_theme_likes_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["theme_id"],
            ["themes.id"],
            name=op.f("fk_theme_likes_theme_id_themes"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "user_id",
            "theme_id",
            name=op.f("pk_theme_likes"),
        ),
    )


def downgrade() -> None:
    op.drop_table("theme_likes")
    op.drop_table("user_active_themes")
    drop_search_vector_index(op, table_name="themes")
    op.drop_index("ix_themes_public_new", table_name="themes")
    op.drop_index("ix_themes_public_popular", table_name="themes")
    op.drop_index("ix_themes_owner", table_name="themes")
    op.drop_index("ix_themes_slug", table_name="themes")
    op.drop_table("themes")
