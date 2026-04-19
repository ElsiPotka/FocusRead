from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid7

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class BookAssetId:
    value: UUID

    @classmethod
    def generate(cls) -> BookAssetId:
        return cls(value=uuid7())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class Sha256:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not _SHA256_PATTERN.fullmatch(normalized):
            raise ValueError("Sha256 must be 64 lowercase hexadecimal characters.")
        object.__setattr__(self, "value", normalized)


class BookAssetFormat(StrEnum):
    PDF = "pdf"


@dataclass(frozen=True, slots=True)
class MimeType:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not normalized:
            raise ValueError("Mime type is required.")
        if len(normalized) > 255:
            raise ValueError("Mime type must be 255 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class FileSizeBytes:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("File size must be greater than zero.")


class StorageBackend(StrEnum):
    LOCAL = "local"
    S3 = "s3"


@dataclass(frozen=True, slots=True)
class StorageKey:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Storage key is required.")
        if len(normalized) > 2048:
            raise ValueError("Storage key must be 2048 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class OriginalFilename:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Original filename is required.")
        if len(normalized) > 255:
            raise ValueError("Original filename must be 255 characters or less.")
        object.__setattr__(self, "value", normalized)


class ProcessingStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class ProcessingError:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("Processing error cannot be blank.")
        if len(normalized) > 5000:
            raise ValueError("Processing error must be 5000 characters or less.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class PageCount:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("Page count must be greater than zero.")


@dataclass(frozen=True, slots=True)
class WordCount:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Word count cannot be negative.")


@dataclass(frozen=True, slots=True)
class TotalChunks:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Total chunks cannot be negative.")
