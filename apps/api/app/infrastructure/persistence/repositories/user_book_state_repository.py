from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.user_book_state.entities import UserBookState
from app.domain.user_book_state.repositories import UserBookStateRepository
from app.domain.user_book_state.value_objects import (
    PreferredWordsPerFlash,
    PreferredWPM,
)
from app.infrastructure.persistence.models.user_book_state import UserBookStateModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyUserBookStateRepository(UserBookStateRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, state: UserBookState) -> None:
        model = await self.session.get(
            UserBookStateModel,
            (state.user_id.value, state.book_id.value),
        )

        if model is None:
            model = UserBookStateModel(
                user_id=state.user_id.value,
                book_id=state.book_id.value,
                favorited_at=state.favorited_at,
                archived_at=state.archived_at,
                completed_at=state.completed_at,
                last_opened_at=state.last_opened_at,
                preferred_wpm=state.preferred_wpm.value if state.preferred_wpm else None,
                preferred_words_per_flash=(
                    state.preferred_words_per_flash.value
                    if state.preferred_words_per_flash
                    else None
                ),
                skip_images=state.skip_images,
                ramp_up_enabled=state.ramp_up_enabled,
            )
            self.session.add(model)
            return

        model.favorited_at = state.favorited_at
        model.archived_at = state.archived_at
        model.completed_at = state.completed_at
        model.last_opened_at = state.last_opened_at
        model.preferred_wpm = state.preferred_wpm.value if state.preferred_wpm else None
        model.preferred_words_per_flash = (
            state.preferred_words_per_flash.value
            if state.preferred_words_per_flash
            else None
        )
        model.skip_images = state.skip_images
        model.ramp_up_enabled = state.ramp_up_enabled

    async def get(
        self, *, user_id: UserId, book_id: BookId
    ) -> UserBookState | None:
        model = await self.session.get(
            UserBookStateModel,
            (user_id.value, book_id.value),
        )
        if model is None:
            return None
        return self._to_entity(model)

    async def list_favorites(self, *, user_id: UserId) -> list[UserBookState]:
        stmt = (
            select(UserBookStateModel)
            .where(
                UserBookStateModel.user_id == user_id.value,
                UserBookStateModel.favorited_at.is_not(None),
            )
            .order_by(UserBookStateModel.favorited_at.desc())
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_archived(self, *, user_id: UserId) -> list[UserBookState]:
        stmt = (
            select(UserBookStateModel)
            .where(
                UserBookStateModel.user_id == user_id.value,
                UserBookStateModel.archived_at.is_not(None),
            )
            .order_by(UserBookStateModel.archived_at.desc())
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_completed(self, *, user_id: UserId) -> list[UserBookState]:
        stmt = (
            select(UserBookStateModel)
            .where(
                UserBookStateModel.user_id == user_id.value,
                UserBookStateModel.completed_at.is_not(None),
            )
            .order_by(UserBookStateModel.completed_at.desc())
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    @staticmethod
    def _to_entity(model: UserBookStateModel) -> UserBookState:
        return UserBookState(
            user_id=UserId(model.user_id),
            book_id=BookId(model.book_id),
            favorited_at=model.favorited_at,
            archived_at=model.archived_at,
            completed_at=model.completed_at,
            last_opened_at=model.last_opened_at,
            preferred_wpm=(
                PreferredWPM(model.preferred_wpm) if model.preferred_wpm else None
            ),
            preferred_words_per_flash=(
                PreferredWordsPerFlash(model.preferred_words_per_flash)
                if model.preferred_words_per_flash
                else None
            ),
            skip_images=model.skip_images,
            ramp_up_enabled=model.ramp_up_enabled,
        )
