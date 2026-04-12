"""refactor reading_sessions to library_item ownership

Revision ID: 0027
Revises: 0026
Create Date: 2026-04-13
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0027"
down_revision: str | None = "0026"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "reading_sessions",
        sa.Column("library_item_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_reading_sessions_library_item_id_library_items"),
        "reading_sessions",
        "library_items",
        ["library_item_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.execute(
        sa.text(
            """
            UPDATE reading_sessions AS session
            SET library_item_id = library_items.id
            FROM library_items
            WHERE session.user_id = library_items.user_id
              AND session.book_id = library_items.book_id
            """
        )
    )

    op.alter_column("reading_sessions", "library_item_id", nullable=False)

    op.drop_constraint(
        "uq_reading_sessions_user_id_book_id",
        "reading_sessions",
        type_="unique",
    )
    op.drop_constraint(
        op.f("fk_reading_sessions_user_id_users"),
        "reading_sessions",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_reading_sessions_book_id_books"),
        "reading_sessions",
        type_="foreignkey",
    )
    op.drop_column("reading_sessions", "user_id")
    op.drop_column("reading_sessions", "book_id")

    op.create_unique_constraint(
        "uq_reading_sessions_library_item_id",
        "reading_sessions",
        ["library_item_id"],
    )


def downgrade() -> None:
    op.add_column("reading_sessions", sa.Column("user_id", sa.UUID(), nullable=True))
    op.add_column("reading_sessions", sa.Column("book_id", sa.UUID(), nullable=True))
    op.drop_constraint(
        "uq_reading_sessions_library_item_id",
        "reading_sessions",
        type_="unique",
    )
    op.drop_constraint(
        op.f("fk_reading_sessions_library_item_id_library_items"),
        "reading_sessions",
        type_="foreignkey",
    )
    op.drop_column("reading_sessions", "library_item_id")

    op.create_foreign_key(
        op.f("fk_reading_sessions_user_id_users"),
        "reading_sessions",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_reading_sessions_book_id_books"),
        "reading_sessions",
        "books",
        ["book_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_reading_sessions_user_id_book_id",
        "reading_sessions",
        ["user_id", "book_id"],
    )
