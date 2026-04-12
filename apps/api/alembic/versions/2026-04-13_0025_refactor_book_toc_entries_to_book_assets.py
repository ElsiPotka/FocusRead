"""refactor book_toc_entries to book_asset ownership

Revision ID: 0025
Revises: 0024
Create Date: 2026-04-13
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0025"
down_revision: str | None = "0024"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "book_toc_entries",
        sa.Column("book_asset_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_book_toc_entries_book_asset_id_book_assets"),
        "book_toc_entries",
        "book_assets",
        ["book_asset_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.execute(
        sa.text(
            """
            UPDATE book_toc_entries AS toc
            SET book_asset_id = books.primary_asset_id
            FROM books
            WHERE toc.book_id = books.id
            """
        )
    )

    op.alter_column("book_toc_entries", "book_asset_id", nullable=False)

    op.drop_index("ix_book_toc_entries_book_order", table_name="book_toc_entries")
    op.drop_constraint(
        op.f("fk_book_toc_entries_book_id_books"),
        "book_toc_entries",
        type_="foreignkey",
    )
    op.drop_column("book_toc_entries", "book_id")

    op.create_index(
        "ix_book_toc_entries_asset_order",
        "book_toc_entries",
        ["book_asset_id", "order_index"],
    )


def downgrade() -> None:
    op.add_column("book_toc_entries", sa.Column("book_id", sa.UUID(), nullable=True))
    op.drop_index("ix_book_toc_entries_asset_order", table_name="book_toc_entries")
    op.drop_constraint(
        op.f("fk_book_toc_entries_book_asset_id_book_assets"),
        "book_toc_entries",
        type_="foreignkey",
    )
    op.drop_column("book_toc_entries", "book_asset_id")

    op.create_foreign_key(
        op.f("fk_book_toc_entries_book_id_books"),
        "book_toc_entries",
        "books",
        ["book_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_book_toc_entries_book_order",
        "book_toc_entries",
        ["book_id", "order_index"],
    )
