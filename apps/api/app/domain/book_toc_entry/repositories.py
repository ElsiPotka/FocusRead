from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.book_toc_entry.entities import BookTOCEntry
    from app.domain.book_toc_entry.value_objects import BookTOCEntryId
    from app.domain.books.value_objects import BookId


class BookTOCEntryRepository(ABC):
    @abstractmethod
    async def save(self, entry: BookTOCEntry) -> None: ...

    @abstractmethod
    async def get(self, entry_id: BookTOCEntryId) -> BookTOCEntry | None: ...

    @abstractmethod
    async def list_for_book(self, *, book_id: BookId) -> list[BookTOCEntry]: ...

    @abstractmethod
    async def save_many(self, entries: list[BookTOCEntry]) -> None: ...

    @abstractmethod
    async def delete_for_book(self, *, book_id: BookId) -> None: ...
