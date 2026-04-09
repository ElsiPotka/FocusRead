from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.reading_sessions.entities import ReadingSession
from app.domain.reading_sessions.repositories import ReadingSessionRepository
from app.domain.reading_sessions.value_objects import (
    CurrentChunk,
    CurrentWordIndex,
    ReadingSessionId,
    WordsPerFlash,
    WpmSpeed,
)
from app.infrastructure.persistence.models.reading_session import ReadingSessionModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyReadingSessionRepository(ReadingSessionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, session: ReadingSession) -> None:
        model = await self.session.get(ReadingSessionModel, session.id.value)

        if model is None:
            model = ReadingSessionModel(
                id=session.id.value,
                user_id=session.user_id.value,
                book_id=session.book_id.value,
                current_word_index=session.current_word_index.value,
                current_chunk=session.current_chunk.value,
                wpm_speed=session.wpm_speed.value,
                words_per_flash=session.words_per_flash.value,
                last_read_at=session.last_read_at,
                created_at=session.created_at,
                updated_at=session.updated_at,
            )
            self.session.add(model)
            return

        model.current_word_index = session.current_word_index.value
        model.current_chunk = session.current_chunk.value
        model.wpm_speed = session.wpm_speed.value
        model.words_per_flash = session.words_per_flash.value
        model.last_read_at = session.last_read_at
        model.updated_at = session.updated_at

    async def get(self, *, user_id: UserId, book_id: BookId) -> ReadingSession | None:
        stmt = select(ReadingSessionModel).where(
            ReadingSessionModel.user_id == user_id.value,
            ReadingSessionModel.book_id == book_id.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: ReadingSessionModel) -> ReadingSession:
        return ReadingSession(
            id=ReadingSessionId(model.id),
            user_id=UserId(model.user_id),
            book_id=BookId(model.book_id),
            current_word_index=CurrentWordIndex(model.current_word_index),
            current_chunk=CurrentChunk(model.current_chunk),
            wpm_speed=WpmSpeed(model.wpm_speed),
            words_per_flash=WordsPerFlash(model.words_per_flash),
            last_read_at=model.last_read_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
