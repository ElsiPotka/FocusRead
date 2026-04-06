from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.book_toc_entry.entities import BookTOCEntry
    from app.domain.book_toc_entry.value_objects import BookTOCEntryId


class BookTOCEntryRepository(ABC):
    @abstractmethod
    async def save(self, entry: BookTOCEntry) -> None: ...

    @abstractmethod
    async def get(self, entry_id: BookTOCEntryId) -> BookTOCEntry | None: ...
