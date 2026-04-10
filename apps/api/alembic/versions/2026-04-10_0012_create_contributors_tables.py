"""create contributors and book_contributors tables

Revision ID: 0012
Revises: 0011
Create Date: 2026-04-10
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op
from app.infrastructure.persistence.migrations.search import (
    create_search_vector_index,
    drop_search_vector_index,
    search_vector_column,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0012"
down_revision: str | None = "0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "contributors",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("sort_name", sa.String(length=255), nullable=True),
        sa.Column("entity_metadata", JSONB(), nullable=True),
        sa.Column(
            "version",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        search_vector_column(
            searchable_columns=("display_name", "sort_name"),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_contributors")),
    )

    op.create_index(
        "ix_contributors_display_name",
        "contributors",
        ["display_name"],
    )
    create_search_vector_index(op, table_name="contributors")

    op.create_table(
        "book_contributors",
        sa.Column("book_id", sa.UUID(), nullable=False),
        sa.Column("contributor_id", sa.UUID(), nullable=False),
        sa.Column(
            "role",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'author'"),
        ),
        sa.Column(
            "position",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            name=op.f("fk_book_contributors_book_id_books"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["contributor_id"],
            ["contributors.id"],
            name=op.f("fk_book_contributors_contributor_id_contributors"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "book_id",
            "contributor_id",
            "role",
            name=op.f("pk_book_contributors"),
        ),
    )

    op.create_index(
        "ix_book_contributors_book_position",
        "book_contributors",
        ["book_id", "position"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_book_contributors_book_position", table_name="book_contributors"
    )
    op.drop_table("book_contributors")
    drop_search_vector_index(op, table_name="contributors")
    op.drop_index("ix_contributors_display_name", table_name="contributors")
    op.drop_table("contributors")
