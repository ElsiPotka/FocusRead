"""create shelves and shelf_books tables

Revision ID: 0013
Revises: 0012
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

revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "shelves",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("color", sa.String(length=32), nullable=True),
        sa.Column("icon", sa.String(length=64), nullable=True),
        sa.Column(
            "is_pinned",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "version",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        search_vector_column(
            searchable_columns=("name", "description"),
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
            ["user_id"],
            ["users.id"],
            name=op.f("fk_shelves_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_shelves")),
        sa.UniqueConstraint("user_id", "name", name="uq_shelves_user_name"),
    )

    op.create_index(
        "ix_shelves_user_sort_order",
        "shelves",
        ["user_id", "sort_order"],
    )
    create_search_vector_index(op, table_name="shelves")

    op.create_table(
        "shelf_books",
        sa.Column("shelf_id", sa.UUID(), nullable=False),
        sa.Column("book_id", sa.UUID(), nullable=False),
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.ForeignKeyConstraint(
            ["shelf_id"],
            ["shelves.id"],
            name=op.f("fk_shelf_books_shelf_id_shelves"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            name=op.f("fk_shelf_books_book_id_books"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "shelf_id",
            "book_id",
            name=op.f("pk_shelf_books"),
        ),
    )

    op.create_index("ix_shelf_books_book_id", "shelf_books", ["book_id"])


def downgrade() -> None:
    op.drop_index("ix_shelf_books_book_id", table_name="shelf_books")
    op.drop_table("shelf_books")
    drop_search_vector_index(op, table_name="shelves")
    op.drop_index("ix_shelves_user_sort_order", table_name="shelves")
    op.drop_table("shelves")
