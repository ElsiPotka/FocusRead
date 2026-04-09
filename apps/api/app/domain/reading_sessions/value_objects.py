from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid7  # noqa: TC003


@dataclass(frozen=True, slots=True)
class ReadingSessionId:
    value: UUID

    @classmethod
    def generate(cls) -> ReadingSessionId:
        return cls(value=uuid7())


@dataclass(frozen=True, slots=True)
class CurrentWordIndex:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Current word index cannot be negative.")


@dataclass(frozen=True, slots=True)
class CurrentChunk:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Current chunk cannot be negative.")


@dataclass(frozen=True, slots=True)
class WpmSpeed:
    value: int

    def __post_init__(self) -> None:
        if not (50 <= self.value <= 2000):
            raise ValueError("WPM speed must be between 50 and 2000.")


@dataclass(frozen=True, slots=True)
class WordsPerFlash:
    value: int

    def __post_init__(self) -> None:
        if self.value not in (1, 2, 3):
            raise ValueError("Words per flash must be 1, 2, or 3.")
