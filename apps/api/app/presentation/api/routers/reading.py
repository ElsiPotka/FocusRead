from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, Security

from app.application.reading.use_cases import (
    GetReadingSession,
    ProgressUpdate,
    UpsertProgress,
)
from app.infrastructure.cache.redis import get_cache
from app.infrastructure.persistence.unit_of_work import get_uow
from app.presentation.api.middleware.auth import get_current_user
from app.presentation.api.schemas.reading import (
    ReadingSessionResponse,
    UpsertProgressRequest,
)
from app.presentation.api.schemas.response import APIResponse

if TYPE_CHECKING:
    from app.domain.auth.entities import User
    from app.infrastructure.cache.redis_cache import RedisCache

router = APIRouter(prefix="/reading", tags=["reading"])


@router.get("/{book_id}/session")
async def get_session(
    book_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
) -> APIResponse[ReadingSessionResponse | None]:
    use_case = GetReadingSession(uow, cache)
    session = await use_case.execute(
        book_id=book_id,
        user_id=current_user.id.value,
    )
    return APIResponse(
        success=True,
        data=ReadingSessionResponse.from_entity(session) if session else None,
        message="Session retrieved" if session else "No session found",
    )


@router.put("/{book_id}/progress")
async def upsert_progress(
    book_id: UUID,
    body: UpsertProgressRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
) -> APIResponse[ReadingSessionResponse]:
    use_case = UpsertProgress(uow, cache)
    session = await use_case.execute(
        book_id=book_id,
        user_id=current_user.id.value,
        update=ProgressUpdate(
            current_word_index=body.current_word_index,
            current_chunk=body.current_chunk,
            wpm_speed=body.wpm_speed,
            words_per_flash=body.words_per_flash,
            words_read_delta=body.words_read_delta,
            time_spent_delta_sec=body.time_spent_delta_sec,
        ),
    )
    return APIResponse(
        success=True,
        data=ReadingSessionResponse.from_entity(session),
        message="Progress saved",
    )
