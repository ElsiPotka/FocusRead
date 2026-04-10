from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, Security

from app.application.labels import (
    AssignLabel,
    CreateLabel,
    DeleteLabel,
    ListLabels,
    UnassignLabel,
    UpdateLabel,
)
from app.infrastructure.persistence.unit_of_work import get_uow
from app.presentation.api.middleware.auth import get_current_user
from app.presentation.api.schemas.labels import (
    AssignLabelRequest,
    CreateLabelRequest,
    LabelResponse,
    UpdateLabelRequest,
)
from app.presentation.api.schemas.response import (
    APIResponse,
    ListResponse,
    MessageResponse,
)

if TYPE_CHECKING:
    from app.domain.auth.entities import User

router = APIRouter(prefix="/labels", tags=["labels"])


@router.post("")
async def create_label(
    body: CreateLabelRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> APIResponse[LabelResponse]:
    use_case = CreateLabel(uow)
    label = await use_case.execute(
        user_id=current_user.id.value,
        name=body.name,
        color=body.color,
    )
    return APIResponse(
        success=True,
        data=LabelResponse.from_entity(label),
        message="Label created",
    )


@router.get("")
async def list_labels(
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> ListResponse[LabelResponse]:
    use_case = ListLabels(uow)
    labels = await use_case.execute(user_id=current_user.id.value)
    data = [LabelResponse.from_entity(label) for label in labels]
    return ListResponse(
        success=True,
        data=data,
        count=len(data),
        message="Labels retrieved",
    )


@router.patch("/{label_id}")
async def update_label(
    label_id: UUID,
    body: UpdateLabelRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> APIResponse[LabelResponse]:
    use_case = UpdateLabel(uow)
    label = await use_case.execute(
        label_id=label_id,
        user_id=current_user.id.value,
        name=body.name,
        color=body.color,
        clear_color=body.clear_color,
    )
    return APIResponse(
        success=True,
        data=LabelResponse.from_entity(label),
        message="Label updated",
    )


@router.delete("/{label_id}")
async def delete_label(
    label_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = DeleteLabel(uow)
    await use_case.execute(
        label_id=label_id,
        user_id=current_user.id.value,
    )
    return MessageResponse(success=True, message="Label deleted")


# Book-label assignment endpoints (nested under /books)

book_labels_router = APIRouter(prefix="/books", tags=["labels"])


@book_labels_router.post("/{book_id}/labels")
async def assign_label_to_book(
    book_id: UUID,
    body: AssignLabelRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = AssignLabel(uow)
    await use_case.execute(
        book_id=book_id,
        label_id=body.label_id,
        user_id=current_user.id.value,
    )
    return MessageResponse(success=True, message="Label assigned to book")


@book_labels_router.delete("/{book_id}/labels/{label_id}")
async def unassign_label_from_book(
    book_id: UUID,
    label_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = UnassignLabel(uow)
    await use_case.execute(
        book_id=book_id,
        label_id=label_id,
        user_id=current_user.id.value,
    )
    return MessageResponse(success=True, message="Label unassigned from book")
