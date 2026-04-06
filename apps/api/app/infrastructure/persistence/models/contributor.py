from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base import Base
from app.infrastructure.persistence.models.base_model import BaseModel
from app.infrastructure.persistence.models.mixins import (
    MetadataMixin,
    SearchMixin,
    VersionMixin,
)
from app.infrastructure.persistence.models.mixins.search import search_vector_index

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.book import BookModel


class ContributorModel(MetadataMixin, SearchMixin, VersionMixin, BaseModel):
    __tablename__ = "contributors"
    __searchable_fields__ = ("display_name", "sort_name")

    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    book_links: Mapped[list[BookContributorModel]] = relationship(
        back_populates="contributor",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    __table_args__ = (
        Index("ix_contributors_display_name", "display_name"),
        search_vector_index(__tablename__),
    )


class BookContributorModel(Base):
    __tablename__ = "book_contributors"

    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
    )
    contributor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contributors.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
        nullable=False,
        default="author",
        server_default=text("'author'"),
    )
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    book: Mapped[BookModel] = relationship("BookModel", lazy="raise")
    contributor: Mapped[ContributorModel] = relationship(
        back_populates="book_links",
        lazy="raise",
    )

    __table_args__ = (
        Index("ix_book_contributors_book_position", "book_id", "position"),
    )
