from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.domain.book_toc_entry.value_objects import BookTOCEntryId, BookTOCTitle

if TYPE_CHECKING:
    from app.domain.books.value_objects import BookId


class BookTOCEntry:
    def __init__(
        self,
        *,
        id: BookTOCEntryId,
        book_id: BookId,
        title: BookTOCTitle,
        level: int,
        order_index: int,
        parent_id: BookTOCEntryId | None = None,
        page_start: int | None = None,
        start_word_index: int | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        if level <= 0:
            raise ValueError("TOC level must be positive.")
        if order_index < 0:
            raise ValueError("TOC order index cannot be negative.")
        if page_start is not None and page_start <= 0:
            raise ValueError("TOC page start must be positive.")
        if start_word_index is not None and start_word_index < 0:
            raise ValueError("TOC start word index cannot be negative.")

        self._id = id
        self._book_id = book_id
        self._title = title
        self._level = level
        self._order_index = order_index
        self._parent_id = parent_id
        self._page_start = page_start
        self._start_word_index = start_word_index
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        *,
        book_id: BookId,
        title: BookTOCTitle,
        level: int,
        order_index: int,
        parent_id: BookTOCEntryId | None = None,
        page_start: int | None = None,
        start_word_index: int | None = None,
    ) -> BookTOCEntry:
        return cls(
            id=BookTOCEntryId.generate(),
            book_id=book_id,
            title=title,
            level=level,
            order_index=order_index,
            parent_id=parent_id,
            page_start=page_start,
            start_word_index=start_word_index,
        )

    @property
    def id(self) -> BookTOCEntryId:
        return self._id

    @property
    def book_id(self) -> BookId:
        return self._book_id

    @property
    def title(self) -> BookTOCTitle:
        return self._title

    @property
    def level(self) -> int:
        return self._level

    @property
    def order_index(self) -> int:
        return self._order_index

    @property
    def parent_id(self) -> BookTOCEntryId | None:
        return self._parent_id

    @property
    def page_start(self) -> int | None:
        return self._page_start

    @property
    def start_word_index(self) -> int | None:
        return self._start_word_index

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def reposition(
        self,
        *,
        level: int,
        order_index: int,
        parent_id: BookTOCEntryId | None = None,
        page_start: int | None = None,
        start_word_index: int | None = None,
    ) -> None:
        if level <= 0:
            raise ValueError("TOC level must be positive.")
        if order_index < 0:
            raise ValueError("TOC order index cannot be negative.")
        if page_start is not None and page_start <= 0:
            raise ValueError("TOC page start must be positive.")
        if start_word_index is not None and start_word_index < 0:
            raise ValueError("TOC start word index cannot be negative.")

        self._level = level
        self._order_index = order_index
        self._parent_id = parent_id
        self._page_start = page_start
        self._start_word_index = start_word_index
        self._updated_at = datetime.now(UTC)

    def rename(self, title: BookTOCTitle) -> None:
        self._title = title
        self._updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, BookTOCEntry) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
