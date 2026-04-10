from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, Query, Security

from app.application.contributors import (
    AttachContributor,
    DetachContributor,
    ListBookContributors,
    ReorderContributors,
)
from app.infrastructure.persistence.unit_of_work import get_uow
from app.presentation.api.middleware.auth import get_current_user
from app.presentation.api.schemas.contributors import (
    AttachContributorRequest,
    BookContributorResponse,
    ReorderContributorsRequest,
)
from app.presentation.api.schemas.response import ListResponse, MessageResponse

if TYPE_CHECKING:
    from app.domain.auth.entities import User

router = APIRouter(prefix="/books", tags=["contributors"])


@router.get("/{book_id}/contributors")
async def list_book_contributors(
    book_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> ListResponse[BookContributorResponse]:
    use_case = ListBookContributors(uow)
    results = await use_case.execute(
        book_id=book_id,
        owner_user_id=current_user.id.value,
    )
    data = [BookContributorResponse.from_tuple(r) for r in results]
    return ListResponse(
        success=True,
        data=data,
        count=len(data),
        message="Contributors retrieved",
    )


@router.post("/{book_id}/contributors")
async def attach_contributor(
    book_id: UUID,
    body: AttachContributorRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> ListResponse[BookContributorResponse]:
    use_case = AttachContributor(uow)
    results = await use_case.execute(
        book_id=book_id,
        owner_user_id=current_user.id.value,
        contributor_display_name=body.display_name,
        contributor_sort_name=body.sort_name,
        role=body.role,
    )
    data = [BookContributorResponse.from_tuple(r) for r in results]
    return ListResponse(
        success=True,
        data=data,
        count=len(data),
        message="Contributor attached",
    )


@router.patch("/{book_id}/contributors/reorder")
async def reorder_contributors(
    book_id: UUID,
    body: ReorderContributorsRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> ListResponse[BookContributorResponse]:
    use_case = ReorderContributors(uow)
    results = await use_case.execute(
        book_id=book_id,
        owner_user_id=current_user.id.value,
        ordering=[
            {
                "contributor_id": item.contributor_id,
                "role": item.role,
                "position": item.position,
            }
            for item in body.ordering
        ],
    )
    data = [BookContributorResponse.from_tuple(r) for r in results]
    return ListResponse(
        success=True,
        data=data,
        count=len(data),
        message="Contributors reordered",
    )


@router.delete("/{book_id}/contributors/{contributor_id}")
async def detach_contributor(
    book_id: UUID,
    contributor_id: UUID,
    role: str = Query(default="author"),
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = DetachContributor(uow)
    await use_case.execute(
        book_id=book_id,
        owner_user_id=current_user.id.value,
        contributor_id=contributor_id,
        role=role,
    )
    return MessageResponse(success=True, message="Contributor detached")
