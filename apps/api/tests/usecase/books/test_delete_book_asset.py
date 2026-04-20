from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.books.use_cases.delete_book_asset import DeleteBookAsset
from app.application.common.errors import ConflictError
from app.application.common.unit_of_work import AbstractUnitOfWork
from app.domain.auth.value_objects import UserId
from app.domain.book_asset.entities import BookAsset
from app.domain.book_asset.repositories import BookAssetRepository
from app.domain.book_asset.value_objects import (
    BookAssetFormat,
    BookAssetId,
    FileSizeBytes,
    MimeType,
    OriginalFilename,
    ProcessingStatus,
    Sha256,
    StorageBackend,
    StorageKey,
)
from app.domain.books.repositories import BookRepository
from app.infrastructure.storage.file_storage import FileStorage


@pytest.fixture
def book_repo():
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def book_asset_repo():
    return AsyncMock(spec=BookAssetRepository)


@pytest.fixture
def uow(book_repo, book_asset_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.books = book_repo
    mock.book_assets = book_asset_repo
    return mock


@pytest.fixture
def file_storage():
    return AsyncMock(spec=FileStorage)


def _make_asset() -> BookAsset:
    now = datetime.now(UTC)
    asset_id = BookAssetId.generate()
    return BookAsset(
        id=asset_id,
        sha256=Sha256("a" * 64),
        format=BookAssetFormat.PDF,
        mime_type=MimeType("application/pdf"),
        file_size_bytes=FileSizeBytes(42),
        storage_backend=StorageBackend.LOCAL,
        storage_key=StorageKey(f"assets/{asset_id.value}/x.pdf"),
        original_filename=OriginalFilename("x.pdf"),
        created_by_user_id=UserId(uuid4()),
        processing_status=ProcessingStatus.READY,
        created_at=now,
        updated_at=now,
    )


async def test_delete_book_asset_swallows_blob_cleanup_failure(
    uow, book_repo, book_asset_repo, file_storage
):
    asset = _make_asset()
    book_asset_repo.get.return_value = asset
    book_repo.count_referencing_asset.return_value = 0
    file_storage.delete.side_effect = RuntimeError("disk unavailable")

    await DeleteBookAsset(uow, file_storage).execute(asset_id=asset.id)

    book_asset_repo.delete.assert_awaited_once_with(asset_id=asset.id)
    uow.commit.assert_awaited_once()
    file_storage.delete.assert_awaited_once_with(storage_key=asset.storage_key.value)


async def test_delete_book_asset_rejects_referenced_assets(
    uow, book_repo, book_asset_repo, file_storage
):
    asset = _make_asset()
    book_asset_repo.get.return_value = asset
    book_repo.count_referencing_asset.return_value = 1

    with pytest.raises(ConflictError):
        await DeleteBookAsset(uow, file_storage).execute(asset_id=asset.id)

    book_asset_repo.delete.assert_not_awaited()
    uow.commit.assert_not_awaited()
    file_storage.delete.assert_not_awaited()
