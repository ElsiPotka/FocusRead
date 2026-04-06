"""create jwt_signing_keys table

Revision ID: 0005
Revises: 0004
Create Date: 2026-04-06
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "jwt_signing_keys",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("public_key", sa.Text(), nullable=False),
        sa.Column("private_key", sa.Text(), nullable=False),
        sa.Column(
            "algorithm",
            sa.String(length=10),
            server_default="RS256",
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            index=True,
            comment="Record creation timestamp",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record last update timestamp",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_jwt_signing_keys")),
    )
    op.create_index(
        "ix_jwt_signing_keys_active",
        "jwt_signing_keys",
        ["id"],
        unique=True,
        postgresql_where=sa.text("expires_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "ix_jwt_signing_keys_active",
        table_name="jwt_signing_keys",
        postgresql_where=sa.text("expires_at IS NULL"),
    )
    op.drop_table("jwt_signing_keys")
