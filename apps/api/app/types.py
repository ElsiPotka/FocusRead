from __future__ import annotations

from collections.abc import Mapping
from typing import TypedDict

type JSONPrimitive = None | bool | int | float | str
type JSONValue = (
    JSONPrimitive | Mapping[str, JSONValue] | list[JSONValue] | tuple[JSONValue, ...]
)
type JSONObject = dict[str, JSONValue]


class PageMeta(TypedDict):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool
    next_cursor: str | None
    prev_cursor: str | None


class PaginatedResult[T](TypedDict):
    items: list[T]
    meta: PageMeta
