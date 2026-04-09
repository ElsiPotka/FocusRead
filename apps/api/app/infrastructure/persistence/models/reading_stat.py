from __future__ import annotations

import uuid  # noqa: TC003
from datetime import date  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.book import BookModel
    from app.infrastructure.persistence.models.user import UserModel


class ReadingStatModel(BaseModel):
    __tablename__ = "reading_stats"

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
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    words_read: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    time_spent_sec: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    avg_wpm: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped[UserModel] = relationship("UserModel", lazy="raise")
    book: Mapped[BookModel] = relationship("BookModel", lazy="raise")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "book_id",
            "session_date",
            name="uq_reading_stats_user_id_book_id_session_date",
        ),
        CheckConstraint(
            "words_read >= 0",
            name="reading_stats_words_read_non_negative",
        ),
        CheckConstraint(
            "time_spent_sec >= 0",
            name="reading_stats_time_spent_sec_non_negative",
        ),
        CheckConstraint(
            "avg_wpm IS NULL OR avg_wpm > 0",
            name="reading_stats_avg_wpm_positive",
        ),
        Index("ix_reading_stats_user_session_date", "user_id", "session_date"),
    )
