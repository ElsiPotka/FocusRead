"""refactor bookmarks to library_item ownership

Revision ID: 0026
Revises: 0025
Create Date: 2026-04-13
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0026"
down_revision: str | None = "0025"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("bookmarks", sa.Column("library_item_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        op.f("fk_bookmarks_library_item_id_library_items"),
        "bookmarks",
        "library_items",
        ["library_item_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.execute(
        sa.text(
            """
            UPDATE bookmarks AS bookmark
            SET library_item_id = library_items.id
            FROM library_items
            WHERE bookmark.user_id = library_items.user_id
              AND bookmark.book_id = library_items.book_id
            """
        )
    )

    op.alter_column("bookmarks", "library_item_id", nullable=False)

    op.drop_index("ix_bookmarks_user_book_created", table_name="bookmarks")
    op.drop_constraint(
        op.f("fk_bookmarks_user_id_users"),
        "bookmarks",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_bookmarks_book_id_books"),
        "bookmarks",
        type_="foreignkey",
    )
    op.drop_column("bookmarks", "user_id")
    op.drop_column("bookmarks", "book_id")

    op.create_index(
        "ix_bookmarks_library_item_created",
        "bookmarks",
        ["library_item_id", "created_at"],
    )


def downgrade() -> None:
    op.add_column("bookmarks", sa.Column("user_id", sa.UUID(), nullable=True))
    op.add_column("bookmarks", sa.Column("book_id", sa.UUID(), nullable=True))
    op.drop_index("ix_bookmarks_library_item_created", table_name="bookmarks")
    op.drop_constraint(
        op.f("fk_bookmarks_library_item_id_library_items"),
        "bookmarks",
        type_="foreignkey",
    )
    op.drop_column("bookmarks", "library_item_id")

    op.create_foreign_key(
        op.f("fk_bookmarks_user_id_users"),
        "bookmarks",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_bookmarks_book_id_books"),
        "bookmarks",
        "books",
        ["book_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_bookmarks_user_book_created",
        "bookmarks",
        ["user_id", "book_id", "created_at"],
    )
