"""create user_book_state table

Revision ID: 0011
Revises: 0010
Create Date: 2026-04-09
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_book_state",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("book_id", sa.UUID(), nullable=False),
        sa.Column("favorited_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("preferred_wpm", sa.Integer(), nullable=True),
        sa.Column("preferred_words_per_flash", sa.Integer(), nullable=True),
        sa.Column(
            "skip_images",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "ramp_up_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.CheckConstraint(
            "preferred_wpm IS NULL OR preferred_wpm > 0",
            name=op.f("ck_user_book_state_preferred_wpm_positive"),
        ),
        sa.CheckConstraint(
            "preferred_words_per_flash IS NULL OR preferred_words_per_flash IN (1, 2, 3)",
            name=op.f("ck_user_book_state_valid_words_per_flash"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_book_state_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            name=op.f("fk_user_book_state_book_id_books"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "user_id", "book_id", name=op.f("pk_user_book_state")
        ),
    )

    op.create_index(
        "ix_user_book_state_user_last_opened",
        "user_book_state",
        ["user_id", "last_opened_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_user_book_state_user_last_opened", table_name="user_book_state"
    )
    op.drop_table("user_book_state")
