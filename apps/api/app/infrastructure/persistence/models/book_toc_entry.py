from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.book_asset import BookAssetModel


class BookTOCEntryModel(BaseModel):
    __tablename__ = "book_toc_entries"

    book_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("book_assets.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("book_toc_entries.id", ondelete="CASCADE"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_word_index: Mapped[int | None] = mapped_column(Integer, nullable=True)

    book_asset: Mapped[BookAssetModel] = relationship("BookAssetModel", lazy="raise")
    parent: Mapped[BookTOCEntryModel | None] = relationship(
        "BookTOCEntryModel",
        remote_side=lambda: [BookTOCEntryModel.id],
        back_populates="children",
        lazy="raise",
    )
    children: Mapped[list[BookTOCEntryModel]] = relationship(
        "BookTOCEntryModel",
        back_populates="parent",
        lazy="raise",
    )

    __table_args__ = (
        CheckConstraint("level > 0", name="book_toc_entries_level_positive"),
        CheckConstraint("order_index >= 0", name="book_toc_entries_order_non_negative"),
        CheckConstraint(
            "page_start IS NULL OR page_start > 0",
            name="book_toc_entries_page_start_positive",
        ),
        CheckConstraint(
            "start_word_index IS NULL OR start_word_index >= 0",
            name="book_toc_entries_start_word_non_negative",
        ),
        Index("ix_book_toc_entries_asset_order", "book_asset_id", "order_index"),
    )
