from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number (1-based)")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")
    cursor: str | None = Field(
        None, description="UUIDv7 cursor for deep-page keyset navigation"
    )


class PaginationMeta(BaseModel):
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Is there a next page?")
    has_prev: bool = Field(..., description="Is there a previous page?")
    next_cursor: str | None = Field(
        None, description="UUIDv7 cursor for next page (deep pages)"
    )
    prev_cursor: str | None = Field(
        None, description="UUIDv7 cursor for previous page (deep pages)"
    )


class PaginatedResponse[T](BaseModel):
    items: list[T]
    meta: PaginationMeta

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "items": [{"id": "01961f0e-...", "title": "Book"}],
                "meta": {
                    "page": 1,
                    "per_page": 20,
                    "total": 100,
                    "total_pages": 5,
                    "has_next": True,
                    "has_prev": False,
                    "next_cursor": None,
                    "prev_cursor": None,
                },
            }
        },
    )
