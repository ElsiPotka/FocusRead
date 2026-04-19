from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date  # noqa: TC003
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId
    from app.domain.library_item.value_objects import LibraryItemId
    from app.domain.reading_stats.entities import ReadingStat
    from app.domain.reading_stats.value_objects import SessionDate


class ReadingStatRepository(ABC):
    @abstractmethod
    async def save(self, stat: ReadingStat) -> None: ...

    @abstractmethod
    async def get(
        self, *, library_item_id: LibraryItemId, session_date: SessionDate
    ) -> ReadingStat | None: ...

    @abstractmethod
    async def list_for_library_item(
        self, *, library_item_id: LibraryItemId
    ) -> list[ReadingStat]: ...

    @abstractmethod
    async def list_for_user(
        self, *, user_id: UserId, since: date | None = None
    ) -> list[ReadingStat]: ...
