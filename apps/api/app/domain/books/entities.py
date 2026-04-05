from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from app.domain.books.errors import InvalidBookStateError
from app.domain.books.value_objects import BookFilePath, BookId, BookTitle


class BookStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class Book:
    def __init__(
        self,
        *,
        id: BookId,
        title: BookTitle,
        file_path: BookFilePath,
        status: BookStatus = BookStatus.PENDING,
        created_at: datetime | None = None,
    ) -> None:
        self._id = id
        self._title = title
        self._file_path = file_path
        self._status = status
        self._created_at = created_at or datetime.now(UTC)

    @classmethod
    def create(cls, *, title: BookTitle, file_path: BookFilePath) -> Book:
        return cls(
            id=BookId.generate(),
            title=title,
            file_path=file_path,
            status=BookStatus.PENDING,
        )

    @property
    def id(self) -> BookId:
        return self._id

    @property
    def title(self) -> BookTitle:
        return self._title

    @property
    def file_path(self) -> BookFilePath:
        return self._file_path

    @property
    def status(self) -> BookStatus:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def mark_processing(self) -> None:
        if self._status is not BookStatus.PENDING:
            raise InvalidBookStateError("Only pending books can start processing.")
        self._status = BookStatus.PROCESSING

    def mark_ready(self) -> None:
        if self._status is not BookStatus.PROCESSING:
            raise InvalidBookStateError("Only processing books can become ready.")
        self._status = BookStatus.READY

    def mark_error(self) -> None:
        self._status = BookStatus.ERROR
