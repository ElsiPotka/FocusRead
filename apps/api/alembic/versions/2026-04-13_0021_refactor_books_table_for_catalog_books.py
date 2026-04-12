"""refactor books table for canonical catalog books

Revision ID: 0021
Revises: 0020
Create Date: 2026-04-13
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op
from app.infrastructure.persistence.migrations.search import (
    create_search_vector_index,
    drop_search_vector_index,
    search_vector_column,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0021"
down_revision: str | None = "0020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "books",
        sa.Column("primary_asset_id", sa.UUID(), nullable=True),
    )
    op.add_column(
        "books",
        sa.Column("created_by_user_id", sa.UUID(), nullable=True),
    )

    op.execute(sa.text("UPDATE books SET created_by_user_id = owner_user_id"))

    drop_search_vector_index(op, table_name="books")
    op.drop_index("ix_books_status", table_name="books")
    op.drop_index("ix_books_owner_user_id_created_at", table_name="books")
    op.drop_column("books", "search_vector")

    op.drop_column("books", "processing_error")
    op.drop_column("books", "status")
    op.drop_column("books", "toc_extracted")
    op.drop_column("books", "has_images")
    op.drop_column("books", "total_chunks")
    op.drop_column("books", "word_count")
    op.drop_column("books", "page_count")
    op.drop_column("books", "file_path")
    op.drop_column("books", "source_filename")
    op.drop_constraint(
        op.f("fk_books_owner_user_id_users"),
        "books",
        type_="foreignkey",
    )
    op.drop_column("books", "owner_user_id")

    op.create_foreign_key(
        op.f("fk_books_primary_asset_id_book_assets"),
        "books",
        "book_assets",
        ["primary_asset_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        op.f("fk_books_created_by_user_id_users"),
        "books",
        "users",
        ["created_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.alter_column("books", "primary_asset_id", nullable=False)

    op.create_index(
        "ix_books_primary_asset_id",
        "books",
        ["primary_asset_id"],
        unique=True,
    )
    op.create_index(
        "ix_books_created_by_user_id_created_at",
        "books",
        ["created_by_user_id", "created_at"],
    )

    op.add_column(
        "books",
        search_vector_column(
            searchable_columns=("title", "subtitle", "description", "publisher"),
        ),
    )
    create_search_vector_index(op, table_name="books")


def downgrade() -> None:
    drop_search_vector_index(op, table_name="books")
    op.drop_column("books", "search_vector")

    op.drop_index(
        "ix_books_created_by_user_id_created_at",
        table_name="books",
    )
    op.drop_index("ix_books_primary_asset_id", table_name="books")

    op.drop_constraint(
        op.f("fk_books_created_by_user_id_users"),
        "books",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_books_primary_asset_id_book_assets"),
        "books",
        type_="foreignkey",
    )

    op.add_column("books", sa.Column("owner_user_id", sa.UUID(), nullable=True))
    op.add_column("books", sa.Column("source_filename", sa.String(length=255), nullable=True))
    op.add_column("books", sa.Column("file_path", sa.String(length=2048), nullable=True))
    op.add_column("books", sa.Column("page_count", sa.Integer(), nullable=True))
    op.add_column("books", sa.Column("word_count", sa.Integer(), nullable=True))
    op.add_column("books", sa.Column("total_chunks", sa.Integer(), nullable=True))
    op.add_column(
        "books",
        sa.Column(
            "has_images",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "books",
        sa.Column(
            "toc_extracted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "books",
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
    )
    op.add_column("books", sa.Column("processing_error", sa.Text(), nullable=True))

    op.execute(sa.text("UPDATE books SET owner_user_id = created_by_user_id"))

    op.drop_column("books", "created_by_user_id")
    op.drop_column("books", "primary_asset_id")

    op.create_foreign_key(
        op.f("fk_books_owner_user_id_users"),
        "books",
        "users",
        ["owner_user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_index("ix_books_status", "books", ["status"])
    op.create_index(
        "ix_books_owner_user_id_created_at",
        "books",
        ["owner_user_id", "created_at"],
    )

    op.add_column(
        "books",
        search_vector_column(
            searchable_columns=(
                "title",
                "subtitle",
                "description",
                "publisher",
                "source_filename",
            ),
        ),
    )
    create_search_vector_index(op, table_name="books")
