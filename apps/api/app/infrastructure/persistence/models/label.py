from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, String, text
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
    from app.infrastructure.persistence.models.book import BookModel
    from app.infrastructure.persistence.models.user import UserModel


class LabelModel(SlugMixin, SearchMixin, VersionMixin, BaseModel):
    __tablename__ = "labels"
    __slug_nullable__ = False
    __searchable_fields__ = ("name", "slug")

    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
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
    book_links: Mapped[list[BookLabelModel]] = relationship(
        back_populates="label",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    __table_args__ = (
        Index("ix_labels_slug", "slug"),
        Index("ix_labels_owner_slug", "owner_user_id", "slug"),
        search_vector_index(__tablename__),
    )


class BookLabelModel(Base):
    __tablename__ = "book_labels"

    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
    )
    label_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("labels.id", ondelete="CASCADE"),
        primary_key=True,
    )

    book: Mapped[BookModel] = relationship("BookModel", lazy="raise")
    label: Mapped[LabelModel] = relationship(back_populates="book_links", lazy="raise")
