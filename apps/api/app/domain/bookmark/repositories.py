from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId
    from app.domain.bookmark.entities import Bookmark
    from app.domain.bookmark.value_objects import BookmarkId
    from app.domain.books.value_objects import BookId


class BookmarkRepository(ABC):
    @abstractmethod
    async def save(self, bookmark: Bookmark) -> None: ...

    @abstractmethod
    async def get(self, bookmark_id: BookmarkId) -> Bookmark | None: ...

    @abstractmethod
    async def get_for_owner(
        self, *, bookmark_id: BookmarkId, user_id: UserId
    ) -> Bookmark | None: ...

    @abstractmethod
    async def list_for_book(
        self, *, user_id: UserId, book_id: BookId
    ) -> list[Bookmark]: ...

    @abstractmethod
    async def delete(self, *, bookmark_id: BookmarkId) -> None: ...
