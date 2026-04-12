"""refactor reading_stats to library_item ownership

Revision ID: 0028
Revises: 0027
Create Date: 2026-04-13
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0028"
down_revision: str | None = "0027"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "reading_stats",
        sa.Column("library_item_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_reading_stats_library_item_id_library_items"),
        "reading_stats",
        "library_items",
        ["library_item_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.execute(
        sa.text(
            """
            UPDATE reading_stats AS stat
            SET library_item_id = library_items.id
            FROM library_items
            WHERE stat.user_id = library_items.user_id
              AND stat.book_id = library_items.book_id
            """
        )
    )

    op.alter_column("reading_stats", "library_item_id", nullable=False)

    op.drop_index("ix_reading_stats_user_session_date", table_name="reading_stats")
    op.drop_constraint(
        "uq_reading_stats_user_id_book_id_session_date",
        "reading_stats",
        type_="unique",
    )
    op.drop_constraint(
        op.f("fk_reading_stats_user_id_users"),
        "reading_stats",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_reading_stats_book_id_books"),
        "reading_stats",
        type_="foreignkey",
    )
    op.drop_column("reading_stats", "user_id")
    op.drop_column("reading_stats", "book_id")

    op.create_unique_constraint(
        "uq_reading_stats_library_item_id_session_date",
        "reading_stats",
        ["library_item_id", "session_date"],
    )
    op.create_index(
        "ix_reading_stats_library_item_session_date",
        "reading_stats",
        ["library_item_id", "session_date"],
    )


def downgrade() -> None:
    op.add_column("reading_stats", sa.Column("user_id", sa.UUID(), nullable=True))
    op.add_column("reading_stats", sa.Column("book_id", sa.UUID(), nullable=True))
    op.drop_index(
        "ix_reading_stats_library_item_session_date",
        table_name="reading_stats",
    )
    op.drop_constraint(
        "uq_reading_stats_library_item_id_session_date",
        "reading_stats",
        type_="unique",
    )
    op.drop_constraint(
        op.f("fk_reading_stats_library_item_id_library_items"),
        "reading_stats",
        type_="foreignkey",
    )
    op.drop_column("reading_stats", "library_item_id")

    op.create_foreign_key(
        op.f("fk_reading_stats_user_id_users"),
        "reading_stats",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_reading_stats_book_id_books"),
        "reading_stats",
        "books",
        ["book_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_reading_stats_user_id_book_id_session_date",
        "reading_stats",
        ["user_id", "book_id", "session_date"],
    )
    op.create_index(
        "ix_reading_stats_user_session_date",
        "reading_stats",
        ["user_id", "session_date"],
    )
