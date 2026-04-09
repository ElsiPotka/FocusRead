from __future__ import annotations

from datetime import date  # noqa: TC003
from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, Query, Security

from app.application.reading.use_cases import GetBookStats, GetStatsSummary
from app.infrastructure.persistence.unit_of_work import get_uow
from app.presentation.api.middleware.auth import get_current_user
from app.presentation.api.schemas.reading import (
    ReadingStatResponse,
    StatsSummaryResponse,
)
from app.presentation.api.schemas.response import APIResponse, ListResponse

if TYPE_CHECKING:
    from app.domain.auth.entities import User

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary")
async def get_summary(
    since: date | None = Query(None),
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> APIResponse[StatsSummaryResponse]:
    use_case = GetStatsSummary(uow)
    summary = await use_case.execute(
        user_id=current_user.id.value,
        since=since,
    )
    return APIResponse(
        success=True,
        data=StatsSummaryResponse.from_model(summary),
        message="Stats summary retrieved",
    )


@router.get("/book/{book_id}")
async def get_book_stats(
    book_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> ListResponse[ReadingStatResponse]:
    use_case = GetBookStats(uow)
    stats = await use_case.execute(
        book_id=book_id,
        user_id=current_user.id.value,
    )
    return ListResponse(
        success=True,
        data=[ReadingStatResponse.from_entity(s) for s in stats],
        count=len(stats),
        message="Book stats retrieved",
    )
