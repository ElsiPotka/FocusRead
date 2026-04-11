"""create book_toc_entries table

Revision ID: 0015
Revises: 0014
Create Date: 2026-04-11
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0015"
down_revision: str | None = "0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "book_toc_entries",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("book_id", sa.UUID(), nullable=False),
        sa.Column("parent_id", sa.UUID(), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("page_start", sa.Integer(), nullable=True),
        sa.Column("start_word_index", sa.Integer(), nullable=True),
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
            ["book_id"],
            ["books.id"],
            name=op.f("fk_book_toc_entries_book_id_books"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["book_toc_entries.id"],
            name=op.f("fk_book_toc_entries_parent_id_book_toc_entries"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_book_toc_entries")),
        sa.CheckConstraint("level > 0", name="book_toc_entries_level_positive"),
        sa.CheckConstraint(
            "order_index >= 0", name="book_toc_entries_order_non_negative"
        ),
        sa.CheckConstraint(
            "page_start IS NULL OR page_start > 0",
            name="book_toc_entries_page_start_positive",
        ),
        sa.CheckConstraint(
            "start_word_index IS NULL OR start_word_index >= 0",
            name="book_toc_entries_start_word_non_negative",
        ),
    )

    op.create_index(
        "ix_book_toc_entries_book_order",
        "book_toc_entries",
        ["book_id", "order_index"],
    )


def downgrade() -> None:
    op.drop_index("ix_book_toc_entries_book_order", table_name="book_toc_entries")
    op.drop_table("book_toc_entries")
