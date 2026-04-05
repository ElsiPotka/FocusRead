from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.books.entities import Book
    from app.domain.books.value_objects import BookId


class BookRepository(ABC):
    @abstractmethod
    async def save(self, book: Book) -> None: ...

    @abstractmethod
    async def get(self, book_id: BookId) -> Book | None: ...
