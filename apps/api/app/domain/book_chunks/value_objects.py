from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid7


@dataclass(frozen=True, slots=True)
class BookChunkId:
    value: UUID

    @classmethod
    def generate(cls) -> BookChunkId:
        return cls(value=uuid7())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class ChunkIndex:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Chunk index cannot be negative.")


@dataclass(frozen=True, slots=True)
class StartWordIndex:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Start word index cannot be negative.")


@dataclass(frozen=True, slots=True)
class ChunkWordCount:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("Chunk word count must be greater than zero.")


@dataclass(frozen=True, slots=True)
class ChunkWordData:
    value: list[list]

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Chunk word data cannot be empty.")
