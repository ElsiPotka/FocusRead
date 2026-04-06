from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, Security

from app.application.books.use_cases import (
    DeleteBook,
    GetBook,
    ListBooks,
    UpdateBookMetadata,
)
from app.infrastructure.persistence.unit_of_work import get_uow
from app.presentation.api.middleware.auth import get_current_user
from app.presentation.api.schemas.books import BookResponse, UpdateBookRequest
from app.presentation.api.schemas.response import (
    APIResponse,
    ListResponse,
    MessageResponse,
)

if TYPE_CHECKING:
    from app.domain.auth.entities import User

router = APIRouter(prefix="/books", tags=["books"])


@router.get("")
async def list_books(
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> ListResponse[BookResponse]:
    use_case = ListBooks(uow)
    books = await use_case.execute(owner_user_id=current_user.id.value)
    return ListResponse(
        success=True,
        data=[BookResponse.from_entity(book) for book in books],
        count=len(books),
        message="Books retrieved",
    )


@router.get("/{book_id}")
async def get_book(
    book_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> APIResponse[BookResponse]:
    use_case = GetBook(uow)
    book = await use_case.execute(
        book_id=book_id,
        owner_user_id=current_user.id.value,
    )
    return APIResponse(
        success=True,
        data=BookResponse.from_entity(book),
        message="Book retrieved",
    )


@router.patch("/{book_id}")
async def update_book(
    book_id: UUID,
    body: UpdateBookRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> APIResponse[BookResponse]:
    use_case = UpdateBookMetadata(uow)
    book = await use_case.execute(
        book_id=book_id,
        owner_user_id=current_user.id.value,
        updates=body.model_dump(exclude_unset=True, mode="python"),
    )
    return APIResponse(
        success=True,
        data=BookResponse.from_entity(book),
        message="Book updated",
    )


@router.delete("/{book_id}")
async def delete_book(
    book_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = DeleteBook(uow)
    await use_case.execute(
        book_id=book_id,
        owner_user_id=current_user.id.value,
    )
    return MessageResponse(success=True, message="Book deleted")
