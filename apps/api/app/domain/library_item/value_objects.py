from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid7


@dataclass(frozen=True, slots=True)
class LibraryItemId:
    value: UUID

    @classmethod
    def generate(cls) -> LibraryItemId:
        return cls(value=uuid7())

    def __str__(self) -> str:
        return str(self.value)


class LibrarySourceKind(StrEnum):
    UPLOAD = "upload"
    PURCHASE = "purchase"
    PROMO = "promo"
    ADMIN_GRANT = "admin_grant"
    SELLER_COPY = "seller_copy"


class AccessStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass(frozen=True, slots=True)
class LibrarySourceRef:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Library source ref cannot be blank.")
        if len(normalized) > 255:
            raise ValueError("Library source ref must be 255 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class RevocationReason:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Revocation reason cannot be blank.")
        if len(normalized) > 5000:
            raise ValueError("Revocation reason must be 5000 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class PreferredWPM:
    value: int

    def __post_init__(self) -> None:
        if self.value < 50 or self.value > 2_000:
            raise ValueError("Preferred WPM must be between 50 and 2000.")


@dataclass(frozen=True, slots=True)
class PreferredWordsPerFlash:
    value: int

    def __post_init__(self) -> None:
        if self.value not in {1, 2, 3}:
            raise ValueError("Preferred words per flash must be 1, 2, or 3.")
