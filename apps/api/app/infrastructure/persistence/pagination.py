from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import lazyload

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm.attributes import InstrumentedAttribute
    from sqlalchemy.sql import Select

_MAX_OFFSET_PAGES = 10


def _strip_loader_options(stmt: Select) -> Select:
    descriptions = getattr(stmt, "column_descriptions", [])
    if any(d.get("expr") is d.get("entity") for d in descriptions):
        return stmt.options(lazyload("*"))
    return stmt


async def _get_total(session: AsyncSession, base_select: Select) -> int:
    count_subquery = _strip_loader_options(base_select).order_by(None).alias()
    total_stmt = select(func.count()).select_from(count_subquery)
    return (await session.execute(total_stmt)).scalar() or 0


def _empty_page(
    page: int, per_page: int, total: int, total_pages: int
) -> dict[str, Any]:
    return {
        "items": [],
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": False,
            "has_prev": page > 1,
            "next_cursor": None,
            "prev_cursor": None,
        },
    }


async def _offset_page(
    session: AsyncSession,
    base_select: Select,
    id_column: InstrumentedAttribute,
    *,
    page: int,
    per_page: int,
    total: int,
    total_pages: int,
    ascending: bool,
) -> dict[str, Any]:
    order = asc(id_column) if ascending else desc(id_column)
    stmt = base_select.order_by(order).limit(per_page).offset((page - 1) * per_page)
    items = list((await session.execute(stmt)).unique().scalars().all())

    return {
        "items": items,
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "next_cursor": None,
            "prev_cursor": None,
        },
    }


async def _keyset_page(
    session: AsyncSession,
    base_select: Select,
    id_column: InstrumentedAttribute,
    *,
    cursor_id: uuid.UUID,
    per_page: int,
    ascending: bool,
) -> tuple[list[Any], bool, str | None, str | None]:
    if ascending:
        stmt = base_select.where(id_column > cursor_id).order_by(asc(id_column))
    else:
        stmt = base_select.where(id_column < cursor_id).order_by(desc(id_column))

    stmt = stmt.limit(per_page + 1)
    items = list((await session.execute(stmt)).unique().scalars().all())

    has_more = len(items) > per_page
    if has_more:
        items = items[:per_page]

    next_cursor = str(getattr(items[-1], id_column.key)) if items and has_more else None
    prev_cursor = str(getattr(items[0], id_column.key)) if items else None

    return items, has_more, next_cursor, prev_cursor


async def paginate(
    session: AsyncSession,
    base_select: Select,
    id_column: InstrumentedAttribute,
    *,
    page: int = 1,
    per_page: int = 20,
    ascending: bool = True,
    cursor: str | None = None,
    max_offset_pages: int = _MAX_OFFSET_PAGES,
) -> dict[str, Any]:
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 20

    total = await _get_total(session, base_select)
    total_pages = (total + per_page - 1) // per_page if total else 0

    if page > total_pages and total > 0:
        return _empty_page(page, per_page, total, total_pages)

    if page <= max_offset_pages and not cursor:
        return await _offset_page(
            session,
            base_select,
            id_column,
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            ascending=ascending,
        )

    if cursor:
        cursor_id = uuid.UUID(cursor)
    else:
        pivot_stmt = (
            _strip_loader_options(base_select)
            .with_only_columns(id_column)
            .order_by(asc(id_column) if ascending else desc(id_column))
            .limit(1)
            .offset((page - 1) * per_page - 1)
        )
        pivot_row = (await session.execute(pivot_stmt)).scalar()
        if pivot_row is None:
            return _empty_page(page, per_page, total, total_pages)
        cursor_id = pivot_row

    items, _has_more, next_cursor, prev_cursor = await _keyset_page(
        session,
        base_select,
        id_column,
        cursor_id=cursor_id,
        per_page=per_page,
        ascending=ascending,
    )

    if page - 1 <= max_offset_pages:
        prev_cursor = None

    return {
        "items": items,
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "next_cursor": next_cursor,
            "prev_cursor": prev_cursor,
        },
    }
