from __future__ import annotations

import uuid  # noqa: TC003
from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.library_item import LibraryItemModel


class ReadingSessionModel(BaseModel):
    __tablename__ = "reading_sessions"

    library_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("library_items.id", ondelete="CASCADE"),
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

    library_item: Mapped[LibraryItemModel] = relationship(
        "LibraryItemModel",
        lazy="raise",
    )

    __table_args__ = (
        UniqueConstraint(
            "library_item_id",
            name="uq_reading_sessions_library_item_id",
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
