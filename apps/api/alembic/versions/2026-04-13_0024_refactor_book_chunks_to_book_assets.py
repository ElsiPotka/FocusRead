"""refactor book_chunks to book_asset ownership

Revision ID: 0024
Revises: 0023
Create Date: 2026-04-13
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0024"
down_revision: str | None = "0023"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("book_chunks", sa.Column("book_asset_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        op.f("fk_book_chunks_book_asset_id_book_assets"),
        "book_chunks",
        "book_assets",
        ["book_asset_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.execute(
        sa.text(
            """
            UPDATE book_chunks AS chunk
            SET book_asset_id = books.primary_asset_id
            FROM books
            WHERE chunk.book_id = books.id
            """
        )
    )

    op.alter_column("book_chunks", "book_asset_id", nullable=False)

    op.drop_index("ix_book_chunks_book_start_word", table_name="book_chunks")
    op.drop_constraint(
        op.f("uq_book_chunks_book_id_chunk_index"),
        "book_chunks",
        type_="unique",
    )
    op.drop_constraint(
        op.f("fk_book_chunks_book_id_books"),
        "book_chunks",
        type_="foreignkey",
    )
    op.drop_column("book_chunks", "book_id")

    op.create_unique_constraint(
        op.f("uq_book_chunks_book_asset_id_chunk_index"),
        "book_chunks",
        ["book_asset_id", "chunk_index"],
    )
    op.create_index(
        "ix_book_chunks_asset_start_word",
        "book_chunks",
        ["book_asset_id", "start_word_index"],
    )


def downgrade() -> None:
    op.add_column("book_chunks", sa.Column("book_id", sa.UUID(), nullable=True))
    op.drop_index("ix_book_chunks_asset_start_word", table_name="book_chunks")
    op.drop_constraint(
        op.f("uq_book_chunks_book_asset_id_chunk_index"),
        "book_chunks",
        type_="unique",
    )
    op.drop_constraint(
        op.f("fk_book_chunks_book_asset_id_book_assets"),
        "book_chunks",
        type_="foreignkey",
    )
    op.drop_column("book_chunks", "book_asset_id")

    op.create_foreign_key(
        op.f("fk_book_chunks_book_id_books"),
        "book_chunks",
        "books",
        ["book_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        op.f("uq_book_chunks_book_id_chunk_index"),
        "book_chunks",
        ["book_id", "chunk_index"],
    )
    op.create_index(
        "ix_book_chunks_book_start_word",
        "book_chunks",
        ["book_id", "start_word_index"],
    )
