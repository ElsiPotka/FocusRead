from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId


class BookSortField(StrEnum):
    CREATED_AT = "created_at"
    TITLE = "title"
    LAST_OPENED_AT = "last_opened_at"


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True, slots=True)
class BookFilter:
    owner_user_id: UserId

    query: str | None = None

    favorited: bool | None = None
    archived: bool | None = None
    completed: bool | None = None
    continue_reading: bool | None = None

    document_type: str | None = None
    status: str | None = None

    sort_by: BookSortField = BookSortField.CREATED_AT
    sort_dir: SortDirection = SortDirection.DESC

    limit: int | None = None
    offset: int = 0
