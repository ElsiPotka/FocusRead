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
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.book import BookModel
    from app.infrastructure.persistence.models.marketplace_listing import (
        MarketplaceListingModel,
    )
    from app.infrastructure.persistence.models.user import UserModel


class LibraryItemModel(BaseModel):
    __tablename__ = "library_items"

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
    source_listing_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("marketplace_listings.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    source_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    access_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="active",
        server_default=text("'active'"),
    )
    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    revocation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    source_listing: Mapped[MarketplaceListingModel | None] = relationship(
        "MarketplaceListingModel",
        back_populates="library_items",
        lazy="raise",
    )

    __table_args__ = (
        CheckConstraint(
            "source_kind IN ('upload', 'purchase', 'promo', 'admin_grant', 'seller_copy')",
            name="library_items_source_kind_valid",
        ),
        CheckConstraint(
            "access_status IN ('active', 'revoked', 'expired')",
            name="library_items_access_status_valid",
        ),
        CheckConstraint(
            "preferred_wpm IS NULL OR preferred_wpm BETWEEN 50 AND 2000",
            name="library_items_preferred_wpm_range",
        ),
        CheckConstraint(
            "preferred_words_per_flash IS NULL OR preferred_words_per_flash IN (1, 2, 3)",
            name="library_items_words_per_flash_valid",
        ),
        Index(
            "uq_library_items_user_id_book_id_active",
            "user_id",
            "book_id",
            unique=True,
            postgresql_where=text("access_status = 'active'"),
        ),
        Index("ix_library_items_user_last_opened", "user_id", "last_opened_at"),
        Index("ix_library_items_user_access_status", "user_id", "access_status"),
        Index("ix_library_items_source_listing_id", "source_listing_id"),
    )
