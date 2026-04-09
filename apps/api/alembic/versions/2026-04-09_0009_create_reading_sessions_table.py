"""create reading_sessions table

Revision ID: 0009
Revises: 0008
Create Date: 2026-04-09
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reading_sessions",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("book_id", sa.UUID(), nullable=False),
        sa.Column("current_word_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("current_chunk", sa.Integer(), server_default="0", nullable=False),
        sa.Column("wpm_speed", sa.Integer(), server_default="250", nullable=False),
        sa.Column("words_per_flash", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "last_read_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
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
            "current_word_index >= 0",
            name=op.f("ck_reading_sessions_current_word_index_non_negative"),
        ),
        sa.CheckConstraint(
            "current_chunk >= 0",
            name=op.f("ck_reading_sessions_current_chunk_non_negative"),
        ),
        sa.CheckConstraint(
            "wpm_speed BETWEEN 50 AND 2000",
            name=op.f("ck_reading_sessions_wpm_speed_range"),
        ),
        sa.CheckConstraint(
            "words_per_flash IN (1, 2, 3)",
            name=op.f("ck_reading_sessions_words_per_flash_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_reading_sessions_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            name=op.f("fk_reading_sessions_book_id_books"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reading_sessions")),
        sa.UniqueConstraint(
            "user_id",
            "book_id",
            name=op.f("uq_reading_sessions_user_id_book_id"),
        ),
    )

    op.create_index(
        op.f("ix_reading_sessions_created_at"),
        "reading_sessions",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_reading_sessions_created_at"), table_name="reading_sessions")
    op.drop_table("reading_sessions")
