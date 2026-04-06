from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.bookmark.entities import Bookmark
    from app.domain.bookmark.value_objects import BookmarkId


class BookmarkRepository(ABC):
    @abstractmethod
    async def save(self, bookmark: Bookmark) -> None: ...

    @abstractmethod
    async def get(self, bookmark_id: BookmarkId) -> Bookmark | None: ...
