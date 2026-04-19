from __future__ import annotations

from datetime import date  # noqa: TC003
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.domain.library_item.value_objects import LibraryItemId
from app.domain.reading_stats.entities import ReadingStat
from app.domain.reading_stats.repositories import ReadingStatRepository
from app.domain.reading_stats.value_objects import (
    AverageWpm,
    ReadingStatId,
    SessionDate,
    TimeSpentSeconds,
    WordsRead,
)
from app.infrastructure.persistence.models.library_item import LibraryItemModel
from app.infrastructure.persistence.models.reading_stat import ReadingStatModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.domain.auth.value_objects import UserId


class SqlAlchemyReadingStatRepository(ReadingStatRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, stat: ReadingStat) -> None:
        model = await self.session.get(ReadingStatModel, stat.id.value)
        if model is None:
            model = ReadingStatModel(
                id=stat.id.value,
                library_item_id=stat.library_item_id.value,
                session_date=stat.session_date.value,
                words_read=stat.words_read.value,
                time_spent_sec=stat.time_spent_sec.value,
                avg_wpm=stat.avg_wpm.value if stat.avg_wpm else None,
                created_at=stat.created_at,
                updated_at=stat.updated_at,
            )
            self.session.add(model)
            return

        model.library_item_id = stat.library_item_id.value
        model.words_read = stat.words_read.value
        model.time_spent_sec = stat.time_spent_sec.value
        model.avg_wpm = stat.avg_wpm.value if stat.avg_wpm else None
        model.updated_at = stat.updated_at

    async def get(
        self,
        *,
        library_item_id: LibraryItemId,
        session_date: SessionDate,
    ) -> ReadingStat | None:
        stmt = select(ReadingStatModel).where(
            ReadingStatModel.library_item_id == library_item_id.value,
            ReadingStatModel.session_date == session_date.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def list_for_library_item(
        self, *, library_item_id: LibraryItemId
    ) -> list[ReadingStat]:
        stmt = (
            select(ReadingStatModel)
            .where(ReadingStatModel.library_item_id == library_item_id.value)
            .order_by(ReadingStatModel.session_date.desc())
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def list_for_user(
        self, *, user_id: UserId, since: date | None = None
    ) -> list[ReadingStat]:
        stmt = (
            select(ReadingStatModel)
            .join(
                LibraryItemModel,
                LibraryItemModel.id == ReadingStatModel.library_item_id,
            )
            .where(LibraryItemModel.user_id == user_id.value)
        )
        if since is not None:
            stmt = stmt.where(ReadingStatModel.session_date >= since)
        stmt = stmt.order_by(ReadingStatModel.session_date.desc())
        result = await self.session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    @staticmethod
    def _to_entity(model: ReadingStatModel) -> ReadingStat:
        return ReadingStat(
            id=ReadingStatId(model.id),
            library_item_id=LibraryItemId(model.library_item_id),
            session_date=SessionDate(model.session_date),
            words_read=WordsRead(model.words_read),
            time_spent_sec=TimeSpentSeconds(model.time_spent_sec),
            avg_wpm=AverageWpm(model.avg_wpm) if model.avg_wpm else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
