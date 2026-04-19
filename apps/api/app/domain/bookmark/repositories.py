from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.bookmark.entities import Bookmark
    from app.domain.bookmark.value_objects import BookmarkId
    from app.domain.library_item.value_objects import LibraryItemId


class BookmarkRepository(ABC):
    @abstractmethod
    async def save(self, bookmark: Bookmark) -> None: ...

    @abstractmethod
    async def get(self, bookmark_id: BookmarkId) -> Bookmark | None: ...

    @abstractmethod
    async def list_for_library_item(
        self, *, library_item_id: LibraryItemId
    ) -> list[Bookmark]: ...

    @abstractmethod
    async def delete(self, *, bookmark_id: BookmarkId) -> None: ...
