from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.role.value_objects import RoleName
from app.infrastructure.persistence.models.base import Base
from app.infrastructure.persistence.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.user import UserModel


user_roles_table = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class RoleModel(BaseModel):
    __tablename__ = "roles"

    name: Mapped[RoleName] = mapped_column(
        Enum(
            RoleName,
            name="role_name_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        unique=True,
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    users: Mapped[list[UserModel]] = relationship(
        secondary=user_roles_table,
        back_populates="roles",
        lazy="raise",
    )
