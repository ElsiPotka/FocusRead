"""create book_assets table

Revision ID: 0020
Revises: 0019
Create Date: 2026-04-13
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0020"
down_revision: str | None = "0019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "book_assets",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column(
            "format",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'pdf'"),
        ),
        sa.Column("mime_type", sa.String(length=255), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("storage_backend", sa.String(length=32), nullable=False),
        sa.Column("storage_key", sa.String(length=2048), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column(
            "processing_status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("processing_error", sa.Text(), nullable=True),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("word_count", sa.Integer(), nullable=True),
        sa.Column("total_chunks", sa.Integer(), nullable=True),
        sa.Column(
            "has_images",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "toc_extracted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("created_by_user_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(sha256) = 64",
            name=op.f("ck_book_assets_sha256_length_valid"),
        ),
        sa.CheckConstraint(
            "format IN ('pdf')",
            name=op.f("ck_book_assets_format_valid"),
        ),
        sa.CheckConstraint(
            "file_size_bytes > 0",
            name=op.f("ck_book_assets_file_size_bytes_positive"),
        ),
        sa.CheckConstraint(
            "processing_status IN ('pending', 'processing', 'ready', 'error')",
            name=op.f("ck_book_assets_processing_status_valid"),
        ),
        sa.CheckConstraint(
            "page_count IS NULL OR page_count > 0",
            name=op.f("ck_book_assets_page_count_positive"),
        ),
        sa.CheckConstraint(
            "word_count IS NULL OR word_count >= 0",
            name=op.f("ck_book_assets_word_count_non_negative"),
        ),
        sa.CheckConstraint(
            "total_chunks IS NULL OR total_chunks >= 0",
            name=op.f("ck_book_assets_total_chunks_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name=op.f("fk_book_assets_created_by_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_book_assets")),
    )

    op.create_index("ix_book_assets_sha256", "book_assets", ["sha256"], unique=True)
    op.create_index(
        "ix_book_assets_storage_key",
        "book_assets",
        ["storage_key"],
        unique=True,
    )
    op.create_index(
        "ix_book_assets_created_by_user_id_created_at",
        "book_assets",
        ["created_by_user_id", "created_at"],
    )
    op.create_index(
        "ix_book_assets_processing_status",
        "book_assets",
        ["processing_status"],
    )


def downgrade() -> None:
    op.drop_index("ix_book_assets_processing_status", table_name="book_assets")
    op.drop_index(
        "ix_book_assets_created_by_user_id_created_at",
        table_name="book_assets",
    )
    op.drop_index("ix_book_assets_storage_key", table_name="book_assets")
    op.drop_index("ix_book_assets_sha256", table_name="book_assets")
    op.drop_table("book_assets")
