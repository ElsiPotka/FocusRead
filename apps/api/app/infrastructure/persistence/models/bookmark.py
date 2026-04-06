from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.book import BookModel
    from app.infrastructure.persistence.models.user import UserModel


class BookmarkModel(BaseModel):
    __tablename__ = "bookmarks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )
    word_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped[UserModel] = relationship("UserModel", lazy="raise")
    book: Mapped[BookModel] = relationship("BookModel", lazy="raise")

    __table_args__ = (
        CheckConstraint("word_index >= 0", name="bookmarks_word_index_non_negative"),
        CheckConstraint(
            "chunk_index IS NULL OR chunk_index >= 0",
            name="bookmarks_chunk_index_non_negative",
        ),
        CheckConstraint(
            "page_number IS NULL OR page_number > 0",
            name="bookmarks_page_number_positive",
        ),
        Index("ix_bookmarks_user_book_created", "user_id", "book_id", "created_at"),
    )
