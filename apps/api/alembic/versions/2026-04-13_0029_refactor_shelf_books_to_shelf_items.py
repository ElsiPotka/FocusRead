"""replace shelf_books with shelf_items

Revision ID: 0029
Revises: 0028
Create Date: 2026-04-13
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0029"
down_revision: str | None = "0028"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "shelf_items",
        sa.Column("shelf_id", sa.UUID(), nullable=False),
        sa.Column("library_item_id", sa.UUID(), nullable=False),
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
            name=op.f("fk_shelf_items_shelf_id_shelves"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["library_item_id"],
            ["library_items.id"],
            name=op.f("fk_shelf_items_library_item_id_library_items"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "shelf_id",
            "library_item_id",
            name=op.f("pk_shelf_items"),
        ),
    )
    op.create_index(
        "ix_shelf_items_library_item_id",
        "shelf_items",
        ["library_item_id"],
    )

    op.execute(
        sa.text(
            """
            INSERT INTO shelf_items (shelf_id, library_item_id, added_at, sort_order)
            SELECT shelf_books.shelf_id, library_items.id, shelf_books.added_at, shelf_books.sort_order
            FROM shelf_books
            JOIN library_items ON library_items.book_id = shelf_books.book_id
            JOIN shelves ON shelves.id = shelf_books.shelf_id
            WHERE library_items.user_id = shelves.user_id
            """
        )
    )

    op.drop_index("ix_shelf_books_book_id", table_name="shelf_books")
    op.drop_table("shelf_books")


def downgrade() -> None:
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
        sa.PrimaryKeyConstraint("shelf_id", "book_id", name=op.f("pk_shelf_books")),
    )
    op.create_index("ix_shelf_books_book_id", "shelf_books", ["book_id"])

    op.drop_index("ix_shelf_items_library_item_id", table_name="shelf_items")
    op.drop_table("shelf_items")
