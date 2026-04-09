from __future__ import annotations

import uuid  # noqa: TC003
from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.book import BookModel
    from app.infrastructure.persistence.models.user import UserModel


class ReadingSessionModel(BaseModel):
    __tablename__ = "reading_sessions"

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
    current_word_index: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    current_chunk: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    wpm_speed: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="250"
    )
    words_per_flash: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1"
    )
    last_read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    user: Mapped[UserModel] = relationship("UserModel", lazy="raise")
    book: Mapped[BookModel] = relationship("BookModel", lazy="raise")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "book_id",
            name="uq_reading_sessions_user_id_book_id",
        ),
        CheckConstraint(
            "current_word_index >= 0",
            name="reading_sessions_current_word_index_non_negative",
        ),
        CheckConstraint(
            "current_chunk >= 0",
            name="reading_sessions_current_chunk_non_negative",
        ),
        CheckConstraint(
            "wpm_speed BETWEEN 50 AND 2000",
            name="reading_sessions_wpm_speed_range",
        ),
        CheckConstraint(
            "words_per_flash IN (1, 2, 3)",
            name="reading_sessions_words_per_flash_valid",
        ),
    )
