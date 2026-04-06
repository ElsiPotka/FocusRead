from __future__ import annotations

import uuid  # noqa: TC003
from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base import Base
from app.infrastructure.persistence.models.base_model import BaseModel
from app.infrastructure.persistence.models.mixins import SearchMixin, VersionMixin
from app.infrastructure.persistence.models.mixins.search import search_vector_index

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.book import BookModel
    from app.infrastructure.persistence.models.user import UserModel


class ShelfModel(SearchMixin, VersionMixin, BaseModel):
    __tablename__ = "shelves"
    __searchable_fields__ = ("name", "description")

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str | None] = mapped_column(String(32), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_pinned: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    user: Mapped[UserModel] = relationship("UserModel", lazy="raise")
    book_links: Mapped[list[ShelfBookModel]] = relationship(
        back_populates="shelf",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_shelves_user_name"),
        Index("ix_shelves_user_sort_order", "user_id", "sort_order"),
        search_vector_index(__tablename__),
    )


class ShelfBookModel(Base):
    __tablename__ = "shelf_books"

    shelf_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shelves.id", ondelete="CASCADE"),
        primary_key=True,
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    shelf: Mapped[ShelfModel] = relationship(back_populates="book_links", lazy="raise")
    book: Mapped[BookModel] = relationship("BookModel", lazy="raise")

    __table_args__ = (Index("ix_shelf_books_book_id", "book_id"),)
