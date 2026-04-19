from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid7

_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True, slots=True)
class MarketplaceListingId:
    value: UUID

    @classmethod
    def generate(cls) -> MarketplaceListingId:
        return cls(value=uuid7())

    def __str__(self) -> str:
        return str(self.value)


class ListingStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    HIDDEN = "hidden"
    ARCHIVED = "archived"


class ModerationStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class ListingSlug:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not normalized:
            raise ValueError("Listing slug cannot be blank.")
        if len(normalized) > 255:
            raise ValueError("Listing slug must be 255 characters or less.")
        if not _SLUG_PATTERN.match(normalized):
            raise ValueError(
                "Listing slug must be lowercase alphanumeric with single hyphens "
                "between segments (e.g. 'deep-work').",
            )
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class ListingSourceRef:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Listing source ref cannot be blank.")
        if len(normalized) > 255:
            raise ValueError("Listing source ref must be 255 characters or less.")
        object.__setattr__(self, "value", normalized)
