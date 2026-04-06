from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid7


@dataclass(frozen=True, slots=True)
class ContributorId:
    value: UUID

    @classmethod
    def generate(cls) -> ContributorId:
        return cls(value=uuid7())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class ContributorDisplayName:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Contributor display name is required.")
        if len(normalized) > 255:
            raise ValueError("Contributor display name must be 255 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class ContributorSortName:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Contributor sort name cannot be blank.")
        if len(normalized) > 255:
            raise ValueError("Contributor sort name must be 255 characters or less.")
        object.__setattr__(self, "value", normalized)


class ContributorRole(StrEnum):
    AUTHOR = "author"
    EDITOR = "editor"
    TRANSLATOR = "translator"
    ILLUSTRATOR = "illustrator"
    OTHER = "other"
