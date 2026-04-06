"""create users table

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-06
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0002"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("surname", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column(
            "email_verified",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
        sa.Column("image", sa.String(length=2048), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(
        "ix_users_email_lower",
        "users",
        [sa.literal_column("lower(email)")],
        unique=True,
    )
    op.create_index(
        "ix_users_is_active",
        "users",
        ["is_active"],
    )


def downgrade() -> None:
    op.drop_index("ix_users_email_lower", table_name="users")
    op.drop_index("ix_users_is_active", table_name="users")
    op.drop_table("users")
