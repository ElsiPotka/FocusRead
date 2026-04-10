from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from app.domain.auth.value_objects import UserId
    from app.domain.books.value_objects import BookId
    from app.domain.shelf.entities import Shelf
    from app.domain.shelf.value_objects import ShelfId


class ShelfRepository(ABC):
    @abstractmethod
    async def save(self, shelf: Shelf) -> None: ...

    @abstractmethod
    async def get(self, shelf_id: ShelfId) -> Shelf | None: ...

    @abstractmethod
    async def get_for_owner(
        self, *, shelf_id: ShelfId, user_id: UserId
    ) -> Shelf | None: ...

    @abstractmethod
    async def list_for_user(self, *, user_id: UserId) -> list[Shelf]: ...

    @abstractmethod
    async def delete(self, shelf_id: ShelfId) -> None: ...

    @abstractmethod
    async def add_book(
        self, *, shelf_id: ShelfId, book_id: BookId, sort_order: int
    ) -> None: ...

    @abstractmethod
    async def remove_book(
        self, *, shelf_id: ShelfId, book_id: BookId
    ) -> None: ...

    @abstractmethod
    async def list_book_ids(self, *, shelf_id: ShelfId) -> list[UUID]: ...

    @abstractmethod
    async def reorder_shelves(
        self, *, ordering: list[tuple[ShelfId, int]]
    ) -> None: ...

    @abstractmethod
    async def reorder_books(
        self,
        *,
        shelf_id: ShelfId,
        ordering: list[tuple[BookId, int]],
    ) -> None: ...
