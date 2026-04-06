from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid7


@dataclass(frozen=True, slots=True)
class BookTOCEntryId:
    value: UUID

    @classmethod
    def generate(cls) -> BookTOCEntryId:
        return cls(value=uuid7())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class BookTOCTitle:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("TOC entry title is required.")
        if len(normalized) > 500:
            raise ValueError("TOC entry title must be 500 characters or less.")
        object.__setattr__(self, "value", normalized)
