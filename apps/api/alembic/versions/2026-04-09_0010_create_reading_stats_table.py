"""create reading_stats table

Revision ID: 0010
Revises: 0009
Create Date: 2026-04-09
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reading_stats",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("book_id", sa.UUID(), nullable=False),
        sa.Column(
            "session_date",
            sa.Date(),
            server_default=sa.text("CURRENT_DATE"),
            nullable=False,
        ),
        sa.Column("words_read", sa.Integer(), server_default="0", nullable=False),
        sa.Column("time_spent_sec", sa.Integer(), server_default="0", nullable=False),
        sa.Column("avg_wpm", sa.Integer(), nullable=True),
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
            "words_read >= 0",
            name=op.f("ck_reading_stats_words_read_non_negative"),
        ),
        sa.CheckConstraint(
            "time_spent_sec >= 0",
            name=op.f("ck_reading_stats_time_spent_sec_non_negative"),
        ),
        sa.CheckConstraint(
            "avg_wpm IS NULL OR avg_wpm > 0",
            name=op.f("ck_reading_stats_avg_wpm_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_reading_stats_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            name=op.f("fk_reading_stats_book_id_books"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reading_stats")),
        sa.UniqueConstraint(
            "user_id",
            "book_id",
            "session_date",
            name=op.f("uq_reading_stats_user_id_book_id_session_date"),
        ),
    )

    op.create_index(
        op.f("ix_reading_stats_created_at"),
        "reading_stats",
        ["created_at"],
    )
    op.create_index(
        "ix_reading_stats_user_session_date",
        "reading_stats",
        ["user_id", "session_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_reading_stats_user_session_date", table_name="reading_stats")
    op.drop_index(op.f("ix_reading_stats_created_at"), table_name="reading_stats")
    op.drop_table("reading_stats")
