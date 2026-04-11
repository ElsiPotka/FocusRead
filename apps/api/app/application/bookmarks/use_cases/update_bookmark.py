from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.bookmark.value_objects import BookmarkId, BookmarkLabel, BookmarkNote

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.bookmark.entities import Bookmark


@dataclass(frozen=True, slots=True)
class BookmarkUpdate:
    word_index: int | None = None
    chunk_index: int | None = None
    page_number: int | None = None
    label: str | None = None
    note: str | None = None
    clear_label: bool = False
    clear_note: bool = False


class UpdateBookmark:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        bookmark_id: UUID,
        user_id: UUID,
        update: BookmarkUpdate,
    ) -> Bookmark:
        bookmark = await self._uow.bookmarks.get_for_owner(
            bookmark_id=BookmarkId(bookmark_id),
            user_id=UserId(user_id),
        )
        if bookmark is None:
            raise NotFoundError("Bookmark not found")

        if update.word_index is not None:
            bookmark.move_to(
                word_index=update.word_index,
                chunk_index=update.chunk_index,
                page_number=update.page_number,
            )

        new_label = bookmark.label
        new_note = bookmark.note

        if update.clear_label:
            new_label = None
        elif update.label is not None:
            new_label = BookmarkLabel(update.label)

        if update.clear_note:
            new_note = None
        elif update.note is not None:
            new_note = BookmarkNote(update.note)

        if new_label != bookmark.label or new_note != bookmark.note:
            bookmark.annotate(label=new_label, note=new_note)

        await self._uow.bookmarks.save(bookmark)
        await self._uow.commit()

        return bookmark
