from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid7

from app.domain.book_asset.value_objects import (
    OriginalFilename,
    PageCount,
    ProcessingError,
    StorageKey,
    TotalChunks,
    WordCount,
)


@dataclass(frozen=True, slots=True)
class BookId:
    value: UUID

    @classmethod
    def generate(cls) -> BookId:
        return cls(value=uuid7())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class BookTitle:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Book title is required.")
        if len(normalized) > 500:
            raise ValueError("Book title must be 500 characters or less.")
        object.__setattr__(self, "value", normalized)


class BookDocumentType(StrEnum):
    BOOK = "book"
    ARTICLE = "article"
    PAPER = "paper"
    MANUAL = "manual"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class BookSubtitle:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Book subtitle cannot be blank.")
        if len(normalized) > 500:
            raise ValueError("Book subtitle must be 500 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class BookDescription:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Book description cannot be blank.")
        if len(normalized) > 5000:
            raise ValueError("Book description must be 5000 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class BookLanguage:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not normalized:
            raise ValueError("Book language cannot be blank.")
        if len(normalized) > 32:
            raise ValueError("Book language must be 32 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class BookCoverImagePath:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Book cover image path cannot be blank.")
        if len(normalized) > 2048:
            raise ValueError("Book cover image path must be 2048 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class BookPublisher:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Book publisher cannot be blank.")
        if len(normalized) > 255:
            raise ValueError("Book publisher must be 255 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class BookPublishedYear:
    value: int

    def __post_init__(self) -> None:
        if not 1 <= self.value <= 9999:
            raise ValueError("Book published year must be between 1 and 9999.")


# Backward-compatible aliases for the legacy upload/processing shape.
BookFilePath = StorageKey
BookSourceFilename = OriginalFilename
BookPageCount = PageCount
BookWordCount = WordCount
BookTotalChunks = TotalChunks
BookProcessingError = ProcessingError
