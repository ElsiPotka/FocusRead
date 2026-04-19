from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
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

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.book import BookModel
    from app.infrastructure.persistence.models.user import UserModel


class BookAssetModel(BaseModel):
    __tablename__ = "book_assets"

    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    format: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pdf",
        server_default=text("'pdf'"),
    )
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_backend: Mapped[str] = mapped_column(String(32), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(2048), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    processing_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pending",
        server_default=text("'pending'"),
    )
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_by: Mapped[UserModel | None] = relationship("UserModel", lazy="raise")
    primary_book: Mapped[BookModel | None] = relationship(
        "BookModel",
        back_populates="primary_asset",
        uselist=False,
        lazy="raise",
    )

    __table_args__ = (
        CheckConstraint(
            "char_length(sha256) = 64",
            name="book_assets_sha256_length_valid",
        ),
        CheckConstraint(
            "format IN ('pdf')",
            name="book_assets_format_valid",
        ),
        CheckConstraint(
            "file_size_bytes > 0",
            name="book_assets_file_size_bytes_positive",
        ),
        CheckConstraint(
            "processing_status IN ('pending', 'processing', 'ready', 'error')",
            name="book_assets_processing_status_valid",
        ),
        CheckConstraint(
            "page_count IS NULL OR page_count > 0",
            name="book_assets_page_count_positive",
        ),
        CheckConstraint(
            "word_count IS NULL OR word_count >= 0",
            name="book_assets_word_count_non_negative",
        ),
        CheckConstraint(
            "total_chunks IS NULL OR total_chunks >= 0",
            name="book_assets_total_chunks_non_negative",
        ),
        Index("ix_book_assets_sha256", "sha256", unique=True),
        Index("ix_book_assets_storage_key", "storage_key", unique=True),
        Index(
            "ix_book_assets_created_by_user_id_created_at",
            "created_by_user_id",
            "created_at",
        ),
        Index("ix_book_assets_processing_status", "processing_status"),
    )
