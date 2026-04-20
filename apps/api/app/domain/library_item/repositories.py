from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId
    from app.domain.books.value_objects import BookId
    from app.domain.library_item.entities import LibraryItem
    from app.domain.library_item.value_objects import LibraryItemId


class LibraryItemRepository(ABC):
    @abstractmethod
    async def save(self, item: LibraryItem) -> None: ...

    @abstractmethod
    async def get(self, item_id: LibraryItemId) -> LibraryItem | None: ...

    @abstractmethod
    async def get_active_for_user_book(
        self, *, user_id: UserId, book_id: BookId
    ) -> LibraryItem | None:
        """Return the user's active LibraryItem for a book, if any.

        This is the authoritative reader-access check. Uses the partial
        unique index `WHERE access_status = 'active'` on
        `(user_id, book_id)`.
        """

    @abstractmethod
    async def list_for_user(self, *, user_id: UserId) -> list[LibraryItem]: ...

    @abstractmethod
    async def count_active_for_book(self, *, book_id: BookId) -> int:
        """Count non-revoked, non-expired library items referencing a book.

        Used as a reference-safety check when considering whether a
        catalog `Book` can be torn down. Filters on
        `access_status = 'active'`.
        """

    @abstractmethod
    async def delete(self, *, item_id: LibraryItemId) -> None: ...
