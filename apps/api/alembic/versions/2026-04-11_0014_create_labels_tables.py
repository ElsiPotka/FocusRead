"""create labels and book_labels tables

Revision ID: 0014
Revises: 0013
Create Date: 2026-04-11
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op
from app.infrastructure.persistence.migrations.search import (
    create_search_vector_index,
    drop_search_vector_index,
    search_vector_column,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0014"
down_revision: str | None = "0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "labels",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("owner_user_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "slug",
            sa.String(length=255),
            nullable=False,
            comment="URL-friendly identifier",
        ),
        sa.Column("color", sa.String(length=32), nullable=True),
        sa.Column(
            "is_system",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
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
            name=op.f("fk_labels_owner_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_labels")),
    )

    op.create_index("ix_labels_slug", "labels", ["slug"])
    op.create_index("ix_labels_owner_slug", "labels", ["owner_user_id", "slug"])
    create_search_vector_index(op, table_name="labels")

    op.create_table(
        "book_labels",
        sa.Column("book_id", sa.UUID(), nullable=False),
        sa.Column("label_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            name=op.f("fk_book_labels_book_id_books"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["label_id"],
            ["labels.id"],
            name=op.f("fk_book_labels_label_id_labels"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "book_id",
            "label_id",
            name=op.f("pk_book_labels"),
        ),
    )


def downgrade() -> None:
    op.drop_table("book_labels")
    drop_search_vector_index(op, table_name="labels")
    op.drop_index("ix_labels_owner_slug", table_name="labels")
    op.drop_index("ix_labels_slug", table_name="labels")
    op.drop_table("labels")
