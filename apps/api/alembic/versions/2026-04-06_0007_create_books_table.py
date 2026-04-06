"""create books table

Revision ID: 0007
Revises: 0006
Create Date: 2026-04-06
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op
from app.infrastructure.persistence.migrations.search import (
    create_search_vector_index,
    drop_search_vector_index,
    search_vector_column,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("owner_user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("subtitle", sa.String(length=500), nullable=True),
        sa.Column(
            "document_type",
            sa.String(length=32),
            server_default=sa.text("'book'"),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=32), nullable=True),
        sa.Column("source_filename", sa.String(length=255), nullable=True),
        sa.Column("file_path", sa.String(length=2048), nullable=False),
        sa.Column("cover_image_path", sa.String(length=2048), nullable=True),
        sa.Column("publisher", sa.String(length=255), nullable=True),
        sa.Column("published_year", sa.Integer(), nullable=True),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("word_count", sa.Integer(), nullable=True),
        sa.Column("total_chunks", sa.Integer(), nullable=True),
        sa.Column(
            "has_images",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "toc_extracted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column("processing_error", sa.Text(), nullable=True),
        sa.Column("entity_metadata", JSONB(), nullable=True),
        sa.Column(
            "version",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        search_vector_column(
            searchable_columns=(
                "title",
                "subtitle",
                "description",
                "publisher",
                "source_filename",
            )
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
            "published_year IS NULL OR published_year BETWEEN 1 AND 9999",
            name=op.f("ck_books_books_published_year_range"),
        ),
        sa.CheckConstraint(
            "page_count IS NULL OR page_count > 0",
            name=op.f("ck_books_books_page_count_positive"),
        ),
        sa.CheckConstraint(
            "word_count IS NULL OR word_count >= 0",
            name=op.f("ck_books_books_word_count_non_negative"),
        ),
        sa.CheckConstraint(
            "total_chunks IS NULL OR total_chunks >= 0",
            name=op.f("ck_books_books_total_chunks_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_books_owner_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_books")),
    )

    op.create_index(op.f("ix_books_created_at"), "books", ["created_at"])
    op.create_index("ix_books_owner_user_id_created_at", "books", ["owner_user_id", "created_at"])
    op.create_index("ix_books_status", "books", ["status"])
    op.create_index("ix_books_document_type", "books", ["document_type"])

    create_search_vector_index(op, table_name="books")


def downgrade() -> None:
    drop_search_vector_index(op, table_name="books")
    op.drop_index("ix_books_document_type", table_name="books")
    op.drop_index("ix_books_status", table_name="books")
    op.drop_index("ix_books_owner_user_id_created_at", table_name="books")
    op.drop_index(op.f("ix_books_created_at"), table_name="books")
    op.drop_table("books")
