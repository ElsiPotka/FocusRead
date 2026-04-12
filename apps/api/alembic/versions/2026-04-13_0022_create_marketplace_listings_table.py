"""create marketplace_listings table

Revision ID: 0022
Revises: 0021
Create Date: 2026-04-13
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0022"
down_revision: str | None = "0021"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "marketplace_listings",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("merchant_user_id", sa.UUID(), nullable=False),
        sa.Column("book_id", sa.UUID(), nullable=False),
        sa.Column(
            "slug",
            sa.String(length=255),
            nullable=False,
            comment="URL-friendly listing identifier",
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'draft'"),
        ),
        sa.Column(
            "moderation_status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("unpublished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("featured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_ref", sa.String(length=255), nullable=True),
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
            "status IN ('draft', 'published', 'hidden', 'archived')",
            name=op.f("ck_marketplace_listings_status_valid"),
        ),
        sa.CheckConstraint(
            "moderation_status IN ('pending', 'approved', 'rejected')",
            name=op.f("ck_marketplace_listings_moderation_status_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["merchant_user_id"],
            ["users.id"],
            name=op.f("fk_marketplace_listings_merchant_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            name=op.f("fk_marketplace_listings_book_id_books"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_marketplace_listings")),
        sa.UniqueConstraint(
            "merchant_user_id",
            "book_id",
            name=op.f("uq_marketplace_listings_merchant_user_id_book_id"),
        ),
    )

    op.create_index(
        "ix_marketplace_listings_slug",
        "marketplace_listings",
        ["slug"],
        unique=True,
    )
    op.create_index(
        "ix_marketplace_listings_merchant_status",
        "marketplace_listings",
        ["merchant_user_id", "status"],
    )
    op.create_index(
        "ix_marketplace_listings_book_id",
        "marketplace_listings",
        ["book_id"],
    )
    op.create_index(
        "ix_marketplace_listings_published_browse",
        "marketplace_listings",
        [sa.text("published_at DESC")],
        postgresql_where=sa.text(
            "status = 'published' AND moderation_status = 'approved'"
        ),
    )


def downgrade() -> None:
    op.drop_index(
        "ix_marketplace_listings_published_browse",
        table_name="marketplace_listings",
    )
    op.drop_index("ix_marketplace_listings_book_id", table_name="marketplace_listings")
    op.drop_index(
        "ix_marketplace_listings_merchant_status",
        table_name="marketplace_listings",
    )
    op.drop_index("ix_marketplace_listings_slug", table_name="marketplace_listings")
    op.drop_table("marketplace_listings")
