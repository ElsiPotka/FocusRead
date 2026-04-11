from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId
    from app.domain.books.entities import Book
    from app.domain.books.filter import BookFilter
    from app.domain.books.value_objects import BookId


class BookRepository(ABC):
    @abstractmethod
    async def save(self, book: Book) -> None: ...

    @abstractmethod
    async def get(self, book_id: BookId) -> Book | None: ...

    @abstractmethod
    async def get_for_owner(
        self, *, book_id: BookId, owner_user_id: UserId
    ) -> Book | None: ...

    @abstractmethod
    async def list_for_owner(self, *, owner_user_id: UserId) -> list[Book]: ...

    @abstractmethod
    async def search(self, *, book_filter: BookFilter) -> list[Book]: ...

    @abstractmethod
    async def delete(self, *, book_id: BookId) -> None: ...
