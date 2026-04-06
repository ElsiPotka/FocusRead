from __future__ import annotations

import uuid  # noqa: TC003
from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.book import BookModel
    from app.infrastructure.persistence.models.user import UserModel


class UserBookStateModel(Base):
    __tablename__ = "user_book_state"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
    )
    favorited_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_opened_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    preferred_wpm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    preferred_words_per_flash: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    skip_images: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    ramp_up_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    user: Mapped[UserModel] = relationship("UserModel", lazy="raise")
    book: Mapped[BookModel] = relationship("BookModel", lazy="raise")

    __table_args__ = (
        CheckConstraint(
            "preferred_wpm IS NULL OR preferred_wpm > 0",
            name="user_book_state_preferred_wpm_positive",
        ),
        CheckConstraint(
            "preferred_words_per_flash IS NULL OR preferred_words_per_flash IN (1, 2, 3)",
            name="user_book_state_valid_words_per_flash",
        ),
        Index("ix_user_book_state_user_last_opened", "user_id", "last_opened_at"),
    )
