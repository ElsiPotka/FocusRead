from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, Security

from app.application.shelves import (
    AddBookToShelf,
    CreateShelf,
    DeleteShelf,
    GetShelf,
    ListShelves,
    RemoveBookFromShelf,
    ReorderShelfBooks,
    ReorderShelves,
    UpdateShelf,
)
from app.infrastructure.persistence.unit_of_work import get_uow
from app.presentation.api.middleware.auth import get_current_user
from app.presentation.api.schemas.response import (
    APIResponse,
    ListResponse,
    MessageResponse,
)
from app.presentation.api.schemas.shelves import (
    AddBookRequest,
    CreateShelfRequest,
    ReorderShelfBooksRequest,
    ReorderShelvesRequest,
    ShelfResponse,
    UpdateShelfRequest,
)

if TYPE_CHECKING:
    from app.domain.auth.entities import User

router = APIRouter(prefix="/shelves", tags=["shelves"])


@router.post("")
async def create_shelf(
    body: CreateShelfRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> APIResponse[ShelfResponse]:
    use_case = CreateShelf(uow)
    shelf = await use_case.execute(
        user_id=current_user.id.value,
        name=body.name,
        description=body.description,
        color=body.color,
        icon=body.icon,
    )
    return APIResponse(
        success=True,
        data=ShelfResponse.from_entity(shelf),
        message="Shelf created",
    )


@router.get("")
async def list_shelves(
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> ListResponse[ShelfResponse]:
    use_case = ListShelves(uow)
    shelves = await use_case.execute(user_id=current_user.id.value)
    data = [ShelfResponse.from_entity(s) for s in shelves]
    return ListResponse(
        success=True,
        data=data,
        count=len(data),
        message="Shelves retrieved",
    )


@router.get("/{shelf_id}")
async def get_shelf(
    shelf_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> APIResponse[ShelfResponse]:
    use_case = GetShelf(uow)
    shelf = await use_case.execute(
        shelf_id=shelf_id,
        user_id=current_user.id.value,
    )
    return APIResponse(
        success=True,
        data=ShelfResponse.from_entity(shelf),
        message="Shelf retrieved",
    )


@router.patch("/{shelf_id}")
async def update_shelf(
    shelf_id: UUID,
    body: UpdateShelfRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> APIResponse[ShelfResponse]:
    use_case = UpdateShelf(uow)
    shelf = await use_case.execute(
        shelf_id=shelf_id,
        user_id=current_user.id.value,
        name=body.name,
        description=body.description,
        color=body.color,
        icon=body.icon,
        clear_description=body.clear_description,
        clear_color=body.clear_color,
        clear_icon=body.clear_icon,
    )
    return APIResponse(
        success=True,
        data=ShelfResponse.from_entity(shelf),
        message="Shelf updated",
    )


@router.delete("/{shelf_id}")
async def delete_shelf(
    shelf_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = DeleteShelf(uow)
    await use_case.execute(
        shelf_id=shelf_id,
        user_id=current_user.id.value,
    )
    return MessageResponse(success=True, message="Shelf deleted")


@router.post("/{shelf_id}/books")
async def add_book_to_shelf(
    shelf_id: UUID,
    body: AddBookRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = AddBookToShelf(uow)
    await use_case.execute(
        shelf_id=shelf_id,
        book_id=body.book_id,
        user_id=current_user.id.value,
    )
    return MessageResponse(success=True, message="Book added to shelf")


@router.delete("/{shelf_id}/books/{book_id}")
async def remove_book_from_shelf(
    shelf_id: UUID,
    book_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = RemoveBookFromShelf(uow)
    await use_case.execute(
        shelf_id=shelf_id,
        book_id=book_id,
        user_id=current_user.id.value,
    )
    return MessageResponse(success=True, message="Book removed from shelf")


@router.patch("/reorder")
async def reorder_shelves(
    body: ReorderShelvesRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> ListResponse[ShelfResponse]:
    use_case = ReorderShelves(uow)
    shelves = await use_case.execute(
        user_id=current_user.id.value,
        ordering=[
            {"shelf_id": item.shelf_id, "sort_order": item.sort_order}
            for item in body.ordering
        ],
    )
    data = [ShelfResponse.from_entity(s) for s in shelves]
    return ListResponse(
        success=True,
        data=data,
        count=len(data),
        message="Shelves reordered",
    )


@router.patch("/{shelf_id}/books/reorder")
async def reorder_shelf_books(
    shelf_id: UUID,
    body: ReorderShelfBooksRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = ReorderShelfBooks(uow)
    await use_case.execute(
        shelf_id=shelf_id,
        user_id=current_user.id.value,
        ordering=[
            {"book_id": item.book_id, "sort_order": item.sort_order}
            for item in body.ordering
        ],
    )
    return MessageResponse(success=True, message="Books reordered")
