"""create bookmarks table

Revision ID: 0016
Revises: 0015
Create Date: 2026-04-11
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0016"
down_revision: str | None = "0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "bookmarks",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("book_id", sa.UUID(), nullable=False),
        sa.Column("word_index", sa.Integer(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=True),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
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
            name=op.f("fk_bookmarks_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            name=op.f("fk_bookmarks_book_id_books"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bookmarks")),
        sa.CheckConstraint(
            "word_index >= 0", name="bookmarks_word_index_non_negative"
        ),
        sa.CheckConstraint(
            "chunk_index IS NULL OR chunk_index >= 0",
            name="bookmarks_chunk_index_non_negative",
        ),
        sa.CheckConstraint(
            "page_number IS NULL OR page_number > 0",
            name="bookmarks_page_number_positive",
        ),
    )

    op.create_index(
        "ix_bookmarks_user_book_created",
        "bookmarks",
        ["user_id", "book_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_bookmarks_user_book_created", table_name="bookmarks")
    op.drop_table("bookmarks")
