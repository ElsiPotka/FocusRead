from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid7


@dataclass(frozen=True, slots=True)
class BookmarkId:
    value: UUID

    @classmethod
    def generate(cls) -> BookmarkId:
        return cls(value=uuid7())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class BookmarkLabel:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Bookmark label cannot be blank.")
        if len(normalized) > 255:
            raise ValueError("Bookmark label must be 255 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class BookmarkNote:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Bookmark note cannot be blank.")
        if len(normalized) > 5000:
            raise ValueError("Bookmark note must be 5000 characters or less.")
        object.__setattr__(self, "value", normalized)
