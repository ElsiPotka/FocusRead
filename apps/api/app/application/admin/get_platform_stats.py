from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import func, select

from app.infrastructure.persistence.models.book import BookModel
from app.infrastructure.persistence.models.user import UserModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True, slots=True)
class PlatformStats:
    total_users: int
    total_books: int
    books_pending: int
    books_processing: int
    books_ready: int
    books_error: int


class GetPlatformStats:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(self) -> PlatformStats:
        user_count = await self._session.scalar(
            select(func.count()).select_from(UserModel)
        )
        book_count = await self._session.scalar(
            select(func.count()).select_from(BookModel)
        )
        status_rows = await self._session.execute(
            select(BookModel.status, func.count())
            .group_by(BookModel.status)
        )
        status_map: dict[str, int] = {
            row[0]: row[1] for row in status_rows.all()
        }

        return PlatformStats(
            total_users=user_count or 0,
            total_books=book_count or 0,
            books_pending=status_map.get("pending", 0),
            books_processing=status_map.get("processing", 0),
            books_ready=status_map.get("ready", 0),
            books_error=status_map.get("error", 0),
        )
