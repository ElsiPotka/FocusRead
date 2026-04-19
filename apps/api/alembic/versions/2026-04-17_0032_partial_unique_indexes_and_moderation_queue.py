"""partial unique indexes and moderation queue index

Replaces plain unique constraints on `library_items` and `marketplace_listings`
with Postgres partial unique indexes so revoked/expired library items and
archived listings do not block legitimate re-grants or re-listings. Also adds a
supporting index on `marketplace_listings (moderation_status, created_at)` for
the admin moderation queue.

Revision ID: 0032
Revises: 0031
Create Date: 2026-04-17
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0032"
down_revision: str | None = "0031"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "uq_library_items_user_id_book_id",
        "library_items",
        type_="unique",
    )
    op.create_index(
        "uq_library_items_user_id_book_id_active",
        "library_items",
        ["user_id", "book_id"],
        unique=True,
        postgresql_where=sa.text("access_status = 'active'"),
    )

    op.drop_constraint(
        "uq_marketplace_listings_merchant_user_id_book_id",
        "marketplace_listings",
        type_="unique",
    )
    op.create_index(
        "uq_marketplace_listings_merchant_book_active",
        "marketplace_listings",
        ["merchant_user_id", "book_id"],
        unique=True,
        postgresql_where=sa.text("status <> 'archived'"),
    )

    op.create_index(
        "ix_marketplace_listings_moderation_queue",
        "marketplace_listings",
        ["moderation_status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_marketplace_listings_moderation_queue",
        table_name="marketplace_listings",
    )
    op.drop_index(
        "uq_marketplace_listings_merchant_book_active",
        table_name="marketplace_listings",
    )
    op.create_unique_constraint(
        "uq_marketplace_listings_merchant_user_id_book_id",
        "marketplace_listings",
        ["merchant_user_id", "book_id"],
    )

    op.drop_index(
        "uq_library_items_user_id_book_id_active",
        table_name="library_items",
    )
    op.create_unique_constraint(
        "uq_library_items_user_id_book_id",
        "library_items",
        ["user_id", "book_id"],
    )
