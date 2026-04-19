from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.domain.bookmark.value_objects import BookmarkId, BookmarkLabel, BookmarkNote

if TYPE_CHECKING:
    from app.domain.library_item.value_objects import LibraryItemId


class Bookmark:
    """A user-specific bookmark anchored to a `LibraryItem`.

    Re-anchored from `(user_id, book_id)` to `library_item_id` since
    bookmarks are a property of the user's readable copy, not the catalog
    book. Revoking the LibraryItem cascades to its bookmarks.
    """

    def __init__(
        self,
        *,
        id: BookmarkId,
        library_item_id: LibraryItemId,
        word_index: int,
        chunk_index: int | None = None,
        page_number: int | None = None,
        label: BookmarkLabel | None = None,
        note: BookmarkNote | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        if word_index < 0:
            raise ValueError("Bookmark word index cannot be negative.")
        if chunk_index is not None and chunk_index < 0:
            raise ValueError("Bookmark chunk index cannot be negative.")
        if page_number is not None and page_number <= 0:
            raise ValueError("Bookmark page number must be positive.")

        self._id = id
        self._library_item_id = library_item_id
        self._word_index = word_index
        self._chunk_index = chunk_index
        self._page_number = page_number
        self._label = label
        self._note = note
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        *,
        library_item_id: LibraryItemId,
        word_index: int,
        chunk_index: int | None = None,
        page_number: int | None = None,
        label: BookmarkLabel | None = None,
        note: BookmarkNote | None = None,
    ) -> Bookmark:
        return cls(
            id=BookmarkId.generate(),
            library_item_id=library_item_id,
            word_index=word_index,
            chunk_index=chunk_index,
            page_number=page_number,
            label=label,
            note=note,
        )

    @property
    def id(self) -> BookmarkId:
        return self._id

    @property
    def library_item_id(self) -> LibraryItemId:
        return self._library_item_id

    @property
    def word_index(self) -> int:
        return self._word_index

    @property
    def chunk_index(self) -> int | None:
        return self._chunk_index

    @property
    def page_number(self) -> int | None:
        return self._page_number

    @property
    def label(self) -> BookmarkLabel | None:
        return self._label

    @property
    def note(self) -> BookmarkNote | None:
        return self._note

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def move_to(
        self,
        *,
        word_index: int,
        chunk_index: int | None = None,
        page_number: int | None = None,
    ) -> None:
        if word_index < 0:
            raise ValueError("Bookmark word index cannot be negative.")
        if chunk_index is not None and chunk_index < 0:
            raise ValueError("Bookmark chunk index cannot be negative.")
        if page_number is not None and page_number <= 0:
            raise ValueError("Bookmark page number must be positive.")

        self._word_index = word_index
        self._chunk_index = chunk_index
        self._page_number = page_number
        self._updated_at = datetime.now(UTC)

    def annotate(
        self,
        *,
        label: BookmarkLabel | None = None,
        note: BookmarkNote | None = None,
    ) -> None:
        self._label = label
        self._note = note
        self._updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Bookmark) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
