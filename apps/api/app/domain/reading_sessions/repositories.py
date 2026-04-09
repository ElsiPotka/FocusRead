from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId
    from app.domain.books.value_objects import BookId
    from app.domain.reading_sessions.entities import ReadingSession


class ReadingSessionRepository(ABC):
    @abstractmethod
    async def save(self, session: ReadingSession) -> None: ...

    @abstractmethod
    async def get(
        self, *, user_id: UserId, book_id: BookId
    ) -> ReadingSession | None: ...
