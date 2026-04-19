from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base import Base
from app.infrastructure.persistence.models.base_model import BaseModel
from app.infrastructure.persistence.models.mixins import (
    SearchMixin,
    SlugMixin,
    VersionMixin,
)
from app.infrastructure.persistence.models.mixins.search import search_vector_index

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.library_item import LibraryItemModel
    from app.infrastructure.persistence.models.user import UserModel


class LabelModel(SlugMixin, SearchMixin, VersionMixin, BaseModel):
    __tablename__ = "library_labels"
    __slug_nullable__ = False
    __searchable_fields__ = ("name", "slug")

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    color: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    owner: Mapped[UserModel | None] = relationship("UserModel", lazy="raise")
    item_links: Mapped[list[LibraryItemLabelModel]] = relationship(
        back_populates="label",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "slug", name="uq_library_labels_user_id_slug"),
        Index("ix_library_labels_slug", "slug"),
        Index("ix_library_labels_user_slug", "user_id", "slug"),
        Index(
            "ix_library_labels_system_slug",
            "slug",
            unique=True,
            postgresql_where=text("is_system"),
        ),
        CheckConstraint(
            "(is_system AND user_id IS NULL) OR ((NOT is_system) AND user_id IS NOT NULL)",
            name="library_labels_owner_mode_valid",
        ),
        search_vector_index(__tablename__),
    )


class LibraryItemLabelModel(Base):
    __tablename__ = "library_item_labels"

    library_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("library_items.id", ondelete="CASCADE"),
        primary_key=True,
    )
    label_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("library_labels.id", ondelete="CASCADE"),
        primary_key=True,
    )

    library_item: Mapped[LibraryItemModel] = relationship(
        "LibraryItemModel",
        lazy="raise",
    )
    label: Mapped[LabelModel] = relationship(back_populates="item_links", lazy="raise")
