from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid7


@dataclass(frozen=True, slots=True)
class ShelfId:
    value: UUID

    @classmethod
    def generate(cls) -> ShelfId:
        return cls(value=uuid7())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class ShelfName:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Shelf name is required.")
        if len(normalized) > 255:
            raise ValueError("Shelf name must be 255 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class ShelfDescription:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Shelf description cannot be blank.")
        if len(normalized) > 1000:
            raise ValueError("Shelf description must be 1000 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class ShelfColor:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Shelf color cannot be blank.")
        if len(normalized) > 32:
            raise ValueError("Shelf color must be 32 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class ShelfIcon:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Shelf icon cannot be blank.")
        if len(normalized) > 64:
            raise ValueError("Shelf icon must be 64 characters or less.")
        object.__setattr__(self, "value", normalized)
