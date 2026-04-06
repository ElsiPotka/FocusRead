from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
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
    from app.infrastructure.persistence.models.user import UserModel


class BookModel(MetadataMixin, SearchMixin, VersionMixin, BaseModel):
    __tablename__ = "books"
    __searchable_fields__ = (
        "title",
        "subtitle",
        "description",
        "publisher",
        "source_filename",
    )

    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
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
    source_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_path: Mapped[str] = mapped_column(String(2048), nullable=False)
    cover_image_path: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    word_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_chunks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    has_images: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    toc_extracted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pending",
        server_default=text("'pending'"),
    )
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    owner: Mapped[UserModel] = relationship("UserModel", lazy="raise")

    __table_args__ = (
        CheckConstraint(
            "published_year IS NULL OR published_year BETWEEN 1 AND 9999",
            name="books_published_year_range",
        ),
        CheckConstraint(
            "page_count IS NULL OR page_count > 0",
            name="books_page_count_positive",
        ),
        CheckConstraint(
            "word_count IS NULL OR word_count >= 0",
            name="books_word_count_non_negative",
        ),
        CheckConstraint(
            "total_chunks IS NULL OR total_chunks >= 0",
            name="books_total_chunks_non_negative",
        ),
        Index("ix_books_owner_user_id_created_at", "owner_user_id", "created_at"),
        Index("ix_books_status", "status"),
        Index("ix_books_document_type", "document_type"),
        search_vector_index(__tablename__),
    )
