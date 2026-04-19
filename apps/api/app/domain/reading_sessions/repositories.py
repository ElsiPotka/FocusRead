from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.library_item.value_objects import LibraryItemId
    from app.domain.reading_sessions.entities import ReadingSession


class ReadingSessionRepository(ABC):
    @abstractmethod
    async def save(self, session: ReadingSession) -> None: ...

    @abstractmethod
    async def get_for_library_item(
        self, *, library_item_id: LibraryItemId
    ) -> ReadingSession | None: ...
