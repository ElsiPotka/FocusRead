"""create library_items table

Revision ID: 0023
Revises: 0022
Create Date: 2026-04-13
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0023"
down_revision: str | None = "0022"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "library_items",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("book_id", sa.UUID(), nullable=False),
        sa.Column("source_listing_id", sa.UUID(), nullable=True),
        sa.Column("source_kind", sa.String(length=32), nullable=False),
        sa.Column("source_ref", sa.String(length=255), nullable=True),
        sa.Column(
            "access_status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
        sa.Column(
            "acquired_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revocation_reason", sa.Text(), nullable=True),
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
            "source_kind IN ('upload', 'purchase', 'promo', 'admin_grant', 'seller_copy')",
            name=op.f("ck_library_items_source_kind_valid"),
        ),
        sa.CheckConstraint(
            "access_status IN ('active', 'revoked', 'expired')",
            name=op.f("ck_library_items_access_status_valid"),
        ),
        sa.CheckConstraint(
            "preferred_wpm IS NULL OR preferred_wpm BETWEEN 50 AND 2000",
            name=op.f("ck_library_items_preferred_wpm_range"),
        ),
        sa.CheckConstraint(
            "preferred_words_per_flash IS NULL OR preferred_words_per_flash IN (1, 2, 3)",
            name=op.f("ck_library_items_words_per_flash_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_library_items_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            name=op.f("fk_library_items_book_id_books"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_listing_id"],
            ["marketplace_listings.id"],
            name=op.f("fk_library_items_source_listing_id_marketplace_listings"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_library_items")),
        sa.UniqueConstraint("user_id", "book_id", name=op.f("uq_library_items_user_id_book_id")),
    )

    op.create_index(
        "ix_library_items_user_last_opened",
        "library_items",
        ["user_id", "last_opened_at"],
    )
    op.create_index(
        "ix_library_items_user_access_status",
        "library_items",
        ["user_id", "access_status"],
    )
    op.create_index(
        "ix_library_items_source_listing_id",
        "library_items",
        ["source_listing_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_library_items_source_listing_id", table_name="library_items")
    op.drop_index("ix_library_items_user_access_status", table_name="library_items")
    op.drop_index("ix_library_items_user_last_opened", table_name="library_items")
    op.drop_table("library_items")
