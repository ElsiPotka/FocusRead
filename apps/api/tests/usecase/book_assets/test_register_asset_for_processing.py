from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.application.book_assets.use_cases import (
    AssetRegistration,
    RegisterAssetForProcessing,
)
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


@pytest.fixture
def book_asset_repo():
    repo = AsyncMock(spec=BookAssetRepository)
    repo.get_by_sha256.return_value = None
    return repo


@pytest.fixture
def uow(book_asset_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.book_assets = book_asset_repo
    return mock


def _existing_asset(*, status: ProcessingStatus) -> BookAsset:
    now = datetime.now(UTC)
    return BookAsset(
        id=BookAssetId.generate(),
        sha256=Sha256("b" * 64),
        format=BookAssetFormat.PDF,
        mime_type=MimeType("application/pdf"),
        file_size_bytes=FileSizeBytes(100),
        storage_backend=StorageBackend.LOCAL,
        storage_key=StorageKey("assets/old/x.pdf"),
        original_filename=OriginalFilename("x.pdf"),
        created_by_user_id=UserId(uuid4()),
        processing_status=status,
        created_at=now,
        updated_at=now,
    )


async def test_creates_new_asset_when_sha256_not_seen(uow, book_asset_repo):
    registration = AssetRegistration(
        sha256="a" * 64,
        storage_key="assets/new/x.pdf",
        file_size_bytes=42,
        original_filename="x.pdf",
        created_by_user_id=uuid4(),
    )

    result = await RegisterAssetForProcessing(uow).execute(registration)

    assert result.created is True
    assert result.needs_processing is True
    assert result.asset.sha256.value == "a" * 64
    assert result.asset.storage_key.value == "assets/new/x.pdf"
    book_asset_repo.save.assert_awaited_once()


async def test_uses_provided_asset_id_when_supplied(uow):
    pre_id = uuid4()
    registration = AssetRegistration(
        sha256="a" * 64,
        storage_key=f"assets/{pre_id}/x.pdf",
        file_size_bytes=42,
        original_filename="x.pdf",
        asset_id=pre_id,
    )

    result = await RegisterAssetForProcessing(uow).execute(registration)

    assert result.asset.id.value == pre_id


async def test_returns_existing_asset_on_sha256_hit_skips_save(uow, book_asset_repo):
    existing = _existing_asset(status=ProcessingStatus.READY)
    book_asset_repo.get_by_sha256.return_value = existing

    registration = AssetRegistration(
        sha256="b" * 64,
        storage_key="assets/new/x.pdf",
        file_size_bytes=42,
        original_filename="x.pdf",
    )
    result = await RegisterAssetForProcessing(uow).execute(registration)

    assert result.created is False
    assert result.needs_processing is False  # READY → no enqueue
    assert result.asset is existing
    book_asset_repo.save.assert_not_called()


@pytest.mark.parametrize(
    "status",
    [ProcessingStatus.PENDING, ProcessingStatus.PROCESSING, ProcessingStatus.ERROR],
)
async def test_dedup_hit_with_non_ready_status_still_requests_processing(
    uow, book_asset_repo, status
):
    book_asset_repo.get_by_sha256.return_value = _existing_asset(status=status)

    registration = AssetRegistration(
        sha256="b" * 64,
        storage_key="assets/new/x.pdf",
        file_size_bytes=42,
        original_filename="x.pdf",
    )
    result = await RegisterAssetForProcessing(uow).execute(registration)

    assert result.created is False
    assert result.needs_processing is True


@patch("app.workers.task.process_book_asset_task")
def test_enqueue_processing_calls_canonical_celery_task(mock_task):
    asset_id = BookAssetId.generate()
    RegisterAssetForProcessing.enqueue_processing(asset_id)
    mock_task.delay.assert_called_once_with(str(asset_id.value))
