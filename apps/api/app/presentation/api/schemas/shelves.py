from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.domain.shelf.entities import Shelf


class ShelfResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    color: str | None
    icon: str | None
    is_pinned: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_entity(shelf: Shelf) -> ShelfResponse:
        return ShelfResponse(
            id=shelf.id.value,
            name=shelf.name.value,
            description=shelf.description.value if shelf.description else None,
            color=shelf.color.value if shelf.color else None,
            icon=shelf.icon.value if shelf.icon else None,
            is_pinned=shelf.is_pinned,
            sort_order=shelf.sort_order,
            created_at=shelf.created_at,
            updated_at=shelf.updated_at,
        )


class CreateShelfRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    color: str | None = Field(None, max_length=32)
    icon: str | None = Field(None, max_length=64)


class UpdateShelfRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    color: str | None = Field(None, max_length=32)
    icon: str | None = Field(None, max_length=64)
    clear_description: bool = False
    clear_color: bool = False
    clear_icon: bool = False


class AddBookRequest(BaseModel):
    book_id: UUID


class ShelfReorderItem(BaseModel):
    shelf_id: UUID
    sort_order: int = Field(..., ge=0)


class ReorderShelvesRequest(BaseModel):
    ordering: list[ShelfReorderItem]


class BookReorderItem(BaseModel):
    book_id: UUID
    sort_order: int = Field(..., ge=0)


class ReorderShelfBooksRequest(BaseModel):
    ordering: list[BookReorderItem]
