from __future__ import annotations

from dataclasses import dataclass
from datetime import date  # noqa: TC003
from uuid import UUID, uuid7  # noqa: TC003


@dataclass(frozen=True, slots=True)
class ReadingStatId:
    value: UUID

    @classmethod
    def generate(cls) -> ReadingStatId:
        return cls(value=uuid7())


@dataclass(frozen=True, slots=True)
class WordsRead:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Words read cannot be negative.")


@dataclass(frozen=True, slots=True)
class TimeSpentSeconds:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Time spent cannot be negative.")


@dataclass(frozen=True, slots=True)
class AverageWpm:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("Average WPM must be positive.")


@dataclass(frozen=True, slots=True)
class SessionDate:
    value: date

    def __post_init__(self) -> None:
        if self.value > date.today():
            raise ValueError("Session date cannot be in the future.")
