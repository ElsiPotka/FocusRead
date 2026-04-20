from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.domain.auth.value_objects import UserId
from app.domain.book_asset.entities import BookAsset
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
    TotalChunks,
)
from app.workers.task import _maybe_short_circuit_existing_asset


def _make_asset(*, status: ProcessingStatus) -> BookAsset:
    now = datetime.now(UTC)
    return BookAsset(
        id=BookAssetId.generate(),
        sha256=Sha256("a" * 64),
        format=BookAssetFormat.PDF,
        mime_type=MimeType("application/pdf"),
        file_size_bytes=FileSizeBytes(42),
        storage_backend=StorageBackend.LOCAL,
        storage_key=StorageKey("assets/x/book.pdf"),
        original_filename=OriginalFilename("book.pdf"),
        created_by_user_id=UserId(uuid4()),
        processing_status=status,
        total_chunks=TotalChunks(7) if status is ProcessingStatus.READY else None,
        created_at=now,
        updated_at=now,
    )


@patch("app.workers.task._publish_asset_progress", new_callable=AsyncMock)
async def test_short_circuit_ready_asset_publishes_terminal_event(mock_publish):
    asset = _make_asset(status=ProcessingStatus.READY)

    result = await _maybe_short_circuit_existing_asset(
        asset_id=str(asset.id.value),
        asset=asset,
    )

    assert result == {
        "status": "ready",
        "asset_id": str(asset.id.value),
        "chunks": "7",
    }
    mock_publish.assert_awaited_once_with(
        str(asset.id.value),
        status="ready",
        progress=100,
        chunks_ready=7,
        total_chunks=7,
    )


@patch("app.workers.task._publish_asset_progress", new_callable=AsyncMock)
async def test_short_circuit_processing_asset_skips_duplicate_run(mock_publish):
    asset = _make_asset(status=ProcessingStatus.PROCESSING)

    result = await _maybe_short_circuit_existing_asset(
        asset_id=str(asset.id.value),
        asset=asset,
    )

    assert result == {
        "status": "processing",
        "asset_id": str(asset.id.value),
        "reason": "already_processing",
    }
    mock_publish.assert_awaited_once_with(
        str(asset.id.value),
        status="processing",
        progress=0,
        chunks_ready=0,
        total_chunks=None,
    )
