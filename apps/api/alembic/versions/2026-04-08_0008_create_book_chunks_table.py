"""create book_chunks table

Revision ID: 0008
Revises: 0007
Create Date: 2026-04-08
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "book_chunks",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("book_id", sa.UUID(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("start_word_index", sa.Integer(), nullable=False),
        sa.Column("word_data", JSONB(), nullable=False),
        sa.Column("word_count", sa.Integer(), nullable=False),
        sa.Column("page_start", sa.Integer(), nullable=True),
        sa.Column("page_end", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record creation timestamp",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record last update timestamp",
        ),
        sa.CheckConstraint(
            "chunk_index >= 0",
            name=op.f("ck_book_chunks_chunk_index_non_negative"),
        ),
        sa.CheckConstraint(
            "start_word_index >= 0",
            name=op.f("ck_book_chunks_start_word_index_non_negative"),
        ),
        sa.CheckConstraint(
            "word_count > 0",
            name=op.f("ck_book_chunks_word_count_positive"),
        ),
        sa.CheckConstraint(
            "page_start IS NULL OR page_start > 0",
            name=op.f("ck_book_chunks_page_start_positive"),
        ),
        sa.CheckConstraint(
            "page_end IS NULL OR page_end > 0",
            name=op.f("ck_book_chunks_page_end_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            name=op.f("fk_book_chunks_book_id_books"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_book_chunks")),
        sa.UniqueConstraint(
            "book_id", "chunk_index",
            name=op.f("uq_book_chunks_book_id_chunk_index"),
        ),
    )

    op.create_index(
        op.f("ix_book_chunks_created_at"),
        "book_chunks",
        ["created_at"],
    )
    op.create_index(
        "ix_book_chunks_book_start_word",
        "book_chunks",
        ["book_id", "start_word_index"],
    )


def downgrade() -> None:
    op.drop_index("ix_book_chunks_book_start_word", table_name="book_chunks")
    op.drop_index(op.f("ix_book_chunks_created_at"), table_name="book_chunks")
    op.drop_table("book_chunks")
