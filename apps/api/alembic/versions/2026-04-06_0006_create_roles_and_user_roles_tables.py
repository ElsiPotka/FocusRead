"""create roles and user_roles tables

Revision ID: 0006
Revises: 0005
Create Date: 2026-04-06
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa

from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

role_name_enum = sa.Enum(
    "Admin",
    "Merchant",
    "Client",
    name="role_name_enum",
)


def upgrade() -> None:
    bind = op.get_bind()
    role_name_enum.create(bind, checkfirst=True)

    op.create_table(
        "roles",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column("name", role_name_enum, nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_roles")),
        sa.UniqueConstraint("name", name=op.f("uq_roles_name")),
    )

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name=op.f("fk_user_roles_role_id_roles"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_roles_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "role_id", name=op.f("pk_user_roles")),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO roles (name, description)
            VALUES
                ('Admin', 'Full administrative access'),
                ('Merchant', 'Merchant platform access'),
                ('Client', 'Default client access')
            """
        )
    )

    op.execute(
        sa.text(
            """
            INSERT INTO user_roles (user_id, role_id)
            SELECT users.id, roles.id
            FROM users
            JOIN roles ON roles.name = 'Client'
            """
        )
    )


def downgrade() -> None:
    bind = op.get_bind()

    op.drop_table("user_roles")
    op.drop_table("roles")
    role_name_enum.drop(bind, checkfirst=True)
