from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.bookmark.value_objects import BookmarkId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class DeleteBookmark:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        bookmark_id: UUID,
        user_id: UUID,
    ) -> None:
        bookmark = await self._uow.bookmarks.get(bookmark_id=BookmarkId(bookmark_id))
        if bookmark is None:
            raise NotFoundError("Bookmark not found")
        library_item = await self._uow.library_items.get(bookmark.library_item_id)
        if library_item is None or library_item.user_id != UserId(user_id):
            raise NotFoundError("Bookmark not found")

        await self._uow.bookmarks.delete(bookmark_id=bookmark.id)
        await self._uow.commit()
