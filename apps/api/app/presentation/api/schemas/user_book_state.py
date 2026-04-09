from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.domain.user_book_state.entities import UserBookState


class UserBookStateResponse(BaseModel):
    favorited_at: datetime | None
    archived_at: datetime | None
    completed_at: datetime | None
    last_opened_at: datetime | None
    preferred_wpm: int | None
    preferred_words_per_flash: int | None
    skip_images: bool
    ramp_up_enabled: bool

    @staticmethod
    def from_entity(state: UserBookState) -> UserBookStateResponse:
        return UserBookStateResponse(
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


class UpdatePreferencesRequest(BaseModel):
    preferred_wpm: int | None = Field(None, ge=50, le=2000)
    preferred_words_per_flash: int | None = Field(None, ge=1, le=3)
    skip_images: bool | None = None
    ramp_up_enabled: bool | None = None
