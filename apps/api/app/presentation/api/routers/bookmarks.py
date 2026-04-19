from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, Security

from app.application.bookmarks.use_cases import (
    CreateBookmark,
    DeleteBookmark,
    ListBookmarks,
    UpdateBookmark,
)
from app.application.bookmarks.use_cases.update_bookmark import BookmarkUpdate
from app.infrastructure.persistence.unit_of_work import get_uow
from app.presentation.api.middleware.auth import get_current_user
from app.presentation.api.schemas.bookmarks import (
    BookmarkResponse,
    CreateBookmarkRequest,
    UpdateBookmarkRequest,
)
from app.presentation.api.schemas.response import (
    APIResponse,
    ListResponse,
    MessageResponse,
)

if TYPE_CHECKING:
    from app.domain.auth.entities import User

router = APIRouter(prefix="/books", tags=["bookmarks"])


@router.post("/{book_id}/bookmarks")
async def create_bookmark(
    book_id: UUID,
    body: CreateBookmarkRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> APIResponse[BookmarkResponse]:
    use_case = CreateBookmark(uow)
    bookmark = await use_case.execute(
        book_id=book_id,
        user_id=current_user.id.value,
        word_index=body.word_index,
        chunk_index=body.chunk_index,
        page_number=body.page_number,
        label=body.label,
        note=body.note,
    )
    return APIResponse(
        success=True,
        data=BookmarkResponse.from_entity(
            bookmark,
            user_id=current_user.id.value,
            book_id=book_id,
        ),
        message="Bookmark created",
    )


@router.get("/{book_id}/bookmarks")
async def list_bookmarks(
    book_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> ListResponse[BookmarkResponse]:
    use_case = ListBookmarks(uow)
    bookmarks = await use_case.execute(
        book_id=book_id,
        user_id=current_user.id.value,
    )
    data = [
        BookmarkResponse.from_entity(
            b,
            user_id=current_user.id.value,
            book_id=book_id,
        )
        for b in bookmarks
    ]
    return ListResponse(
        success=True,
        data=data,
        count=len(data),
        message="Bookmarks retrieved",
    )


@router.patch("/{book_id}/bookmarks/{bookmark_id}")
async def update_bookmark(
    book_id: UUID,
    bookmark_id: UUID,
    body: UpdateBookmarkRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> APIResponse[BookmarkResponse]:
    use_case = UpdateBookmark(uow)
    bookmark = await use_case.execute(
        bookmark_id=bookmark_id,
        user_id=current_user.id.value,
        update=BookmarkUpdate(
            word_index=body.word_index,
            chunk_index=body.chunk_index,
            page_number=body.page_number,
            label=body.label,
            note=body.note,
            clear_label=body.clear_label,
            clear_note=body.clear_note,
        ),
    )
    return APIResponse(
        success=True,
        data=BookmarkResponse.from_entity(
            bookmark,
            user_id=current_user.id.value,
            book_id=book_id,
        ),
        message="Bookmark updated",
    )


@router.delete("/{book_id}/bookmarks/{bookmark_id}")
async def delete_bookmark(
    book_id: UUID,
    bookmark_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = DeleteBookmark(uow)
    await use_case.execute(
        bookmark_id=bookmark_id,
        user_id=current_user.id.value,
    )
    return MessageResponse(success=True, message="Bookmark deleted")
