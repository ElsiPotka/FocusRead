from __future__ import annotations

import mimetypes
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.infrastructure.persistence.models.book import BookModel
from app.infrastructure.persistence.models.library_item import LibraryItemModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


DEFAULT_ASSET_FORMAT = "pdf"
DEFAULT_ASSET_MIME_TYPE = "application/pdf"
DEFAULT_STORAGE_BACKEND = "local"
DEFAULT_LIBRARY_SOURCE_KIND = "upload"
DEFAULT_LIBRARY_ACCESS_STATUS = "active"


def build_placeholder_sha(*, book_id: uuid.UUID) -> str:
    return f"{book_id.hex}{book_id.hex}"


def detect_mime_type(*, source_filename: str | None, storage_key: str) -> str:
    mime_type, _ = mimetypes.guess_type(source_filename or storage_key)
    return mime_type or DEFAULT_ASSET_MIME_TYPE


def detect_original_filename(*, source_filename: str | None, storage_key: str) -> str:
    if source_filename:
        return source_filename
    name = Path(storage_key).name
    return name or "book.pdf"


def detect_file_size_bytes(*, storage_key: str) -> int:
    try:
        size = Path(storage_key).stat().st_size
    except OSError:
        size = len(storage_key.encode("utf-8"))
    return max(size, 1)


async def resolve_primary_asset_id(
    session: AsyncSession,
    *,
    book_id: uuid.UUID,
) -> uuid.UUID | None:
    stmt = select(BookModel.primary_asset_id).where(BookModel.id == book_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def resolve_book_id_for_asset(
    session: AsyncSession,
    *,
    book_asset_id: uuid.UUID,
) -> uuid.UUID | None:
    stmt = select(BookModel.id).where(BookModel.primary_asset_id == book_asset_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_library_item(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    book_id: uuid.UUID,
) -> LibraryItemModel | None:
    stmt = select(LibraryItemModel).where(
        LibraryItemModel.user_id == user_id,
        LibraryItemModel.book_id == book_id,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def resolve_library_item_id(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    book_id: uuid.UUID,
) -> uuid.UUID | None:
    stmt = select(LibraryItemModel.id).where(
        LibraryItemModel.user_id == user_id,
        LibraryItemModel.book_id == book_id,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def ensure_library_item(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    book_id: uuid.UUID,
    source_kind: str = DEFAULT_LIBRARY_SOURCE_KIND,
    source_ref: str | None = None,
    acquired_at: datetime | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> LibraryItemModel:
    model = await get_library_item(session, user_id=user_id, book_id=book_id)
    if model is not None:
        return model

    now = datetime.now(UTC)
    acquired = acquired_at or created_at or now
    created = created_at or acquired
    updated = updated_at or created
    model = LibraryItemModel(
        id=uuid.uuid7(),
        user_id=user_id,
        book_id=book_id,
        source_kind=source_kind,
        source_ref=source_ref,
        access_status=DEFAULT_LIBRARY_ACCESS_STATUS,
        acquired_at=acquired,
        created_at=created,
        updated_at=updated,
    )
    session.add(model)
    return model
