from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.book_asset import BookAssetModel


class BookChunkModel(BaseModel):
    __tablename__ = "book_chunks"

    book_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("book_assets.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_word_index: Mapped[int] = mapped_column(Integer, nullable=False)
    word_data: Mapped[list] = mapped_column(JSONB, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    book_asset: Mapped[BookAssetModel] = relationship("BookAssetModel", lazy="raise")

    __table_args__ = (
        UniqueConstraint(
            "book_asset_id",
            "chunk_index",
            name="uq_book_chunks_book_asset_id_chunk_index",
        ),
        CheckConstraint(
            "chunk_index >= 0",
            name="book_chunks_chunk_index_non_negative",
        ),
        CheckConstraint(
            "start_word_index >= 0",
            name="book_chunks_start_word_index_non_negative",
        ),
        CheckConstraint(
            "word_count > 0",
            name="book_chunks_word_count_positive",
        ),
        CheckConstraint(
            "page_start IS NULL OR page_start > 0",
            name="book_chunks_page_start_positive",
        ),
        CheckConstraint(
            "page_end IS NULL OR page_end > 0",
            name="book_chunks_page_end_positive",
        ),
        Index("ix_book_chunks_asset_start_word", "book_asset_id", "start_word_index"),
    )
