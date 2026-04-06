from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid7


@dataclass(frozen=True, slots=True)
class LabelId:
    value: UUID

    @classmethod
    def generate(cls) -> LabelId:
        return cls(value=uuid7())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class LabelName:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Label name is required.")
        if len(normalized) > 255:
            raise ValueError("Label name must be 255 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class LabelSlug:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not normalized:
            raise ValueError("Label slug is required.")
        if len(normalized) > 255:
            raise ValueError("Label slug must be 255 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class LabelColor:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Label color cannot be blank.")
        if len(normalized) > 32:
            raise ValueError("Label color must be 32 characters or less.")
        object.__setattr__(self, "value", normalized)
