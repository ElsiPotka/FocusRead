from __future__ import annotations

import uuid  # noqa: TC003
from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.book import BookModel
    from app.infrastructure.persistence.models.library_item import LibraryItemModel
    from app.infrastructure.persistence.models.user import UserModel


class MarketplaceListingModel(BaseModel):
    __tablename__ = "marketplace_listings"

    merchant_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="URL-friendly listing identifier",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="draft",
        server_default=text("'draft'"),
    )
    moderation_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pending",
        server_default=text("'pending'"),
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    unpublished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    featured_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    source_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)

    merchant: Mapped[UserModel] = relationship("UserModel", lazy="raise")
    book: Mapped[BookModel] = relationship("BookModel", lazy="raise")
    library_items: Mapped[list[LibraryItemModel]] = relationship(
        "LibraryItemModel",
        back_populates="source_listing",
        lazy="raise",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'published', 'hidden', 'archived')",
            name="marketplace_listings_status_valid",
        ),
        CheckConstraint(
            "moderation_status IN ('pending', 'approved', 'rejected')",
            name="marketplace_listings_moderation_status_valid",
        ),
        Index(
            "uq_marketplace_listings_merchant_book_active",
            "merchant_user_id",
            "book_id",
            unique=True,
            postgresql_where=text("status <> 'archived'"),
        ),
        Index("ix_marketplace_listings_slug", "slug", unique=True),
        Index(
            "ix_marketplace_listings_merchant_status",
            "merchant_user_id",
            "status",
        ),
        Index("ix_marketplace_listings_book_id", "book_id"),
        Index(
            "ix_marketplace_listings_moderation_queue",
            "moderation_status",
            "created_at",
        ),
    )
