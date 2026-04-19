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
    from app.infrastructure.persistence.models.library_item import LibraryItemModel


class ReadingStatModel(BaseModel):
    __tablename__ = "reading_stats"

    library_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("library_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    words_read: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    time_spent_sec: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    avg_wpm: Mapped[int | None] = mapped_column(Integer, nullable=True)

    library_item: Mapped[LibraryItemModel] = relationship(
        "LibraryItemModel",
        lazy="raise",
    )

    __table_args__ = (
        UniqueConstraint(
            "library_item_id",
            "session_date",
            name="uq_reading_stats_library_item_id_session_date",
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
        Index(
            "ix_reading_stats_library_item_session_date",
            "library_item_id",
            "session_date",
        ),
    )
