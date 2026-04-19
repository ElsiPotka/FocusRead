from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base_model import BaseModel
from app.infrastructure.persistence.models.mixins import (
    MetadataMixin,
    SearchMixin,
    VersionMixin,
)
from app.infrastructure.persistence.models.mixins.search import search_vector_index

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.book_asset import BookAssetModel
    from app.infrastructure.persistence.models.user import UserModel


class BookModel(MetadataMixin, SearchMixin, VersionMixin, BaseModel):
    __tablename__ = "books"
    __searchable_fields__ = (
        "title",
        "subtitle",
        "description",
        "publisher",
    )

    primary_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("book_assets.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(500), nullable=True)
    document_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="book",
        server_default=text("'book'"),
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    cover_image_path: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    primary_asset: Mapped[BookAssetModel] = relationship(
        "BookAssetModel",
        back_populates="primary_book",
        lazy="raise",
    )
    created_by: Mapped[UserModel | None] = relationship("UserModel", lazy="raise")

    __table_args__ = (
        CheckConstraint(
            "published_year IS NULL OR published_year BETWEEN 1 AND 9999",
            name="books_published_year_range",
        ),
        Index("ix_books_primary_asset_id", "primary_asset_id", unique=True),
        Index(
            "ix_books_created_by_user_id_created_at",
            "created_by_user_id",
            "created_at",
        ),
        Index("ix_books_document_type", "document_type"),
        search_vector_index(__tablename__),
    )
