from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.application.books.use_cases.register_book_upload import RegisterBookUpload
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
from app.domain.library_item.repositories import LibraryItemRepository
from app.infrastructure.storage.file_storage import FileStorage


@pytest.fixture
def book_repo():
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def book_asset_repo():
    repo = AsyncMock(spec=BookAssetRepository)
    repo.get_by_sha256.return_value = None
    return repo


@pytest.fixture
def library_item_repo():
    return AsyncMock(spec=LibraryItemRepository)


@pytest.fixture
def uow(book_repo, book_asset_repo, library_item_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.books = book_repo
    mock.book_assets = book_asset_repo
    mock.library_items = library_item_repo
    return mock


@pytest.fixture
def file_storage():
    storage = AsyncMock(spec=FileStorage)
    storage.delete.return_value = None
    return storage


def _existing_asset(*, storage_key: str) -> BookAsset:
    now = datetime.now(UTC)
    return BookAsset(
        id=BookAssetId.generate(),
        sha256=Sha256("b" * 64),
        format=BookAssetFormat.PDF,
        mime_type=MimeType("application/pdf"),
        file_size_bytes=FileSizeBytes(100),
        storage_backend=StorageBackend.LOCAL,
        storage_key=StorageKey(storage_key),
        original_filename=OriginalFilename("x.pdf"),
        created_by_user_id=UserId(uuid4()),
        processing_status=ProcessingStatus.READY,
        created_at=now,
        updated_at=now,
    )


@patch("app.workers.task.process_book_asset_task")
async def test_register_book_upload_creates_asset_book_and_library_item(
    mock_task,
    uow, book_asset_repo, book_repo, library_item_repo, file_storage
):
    result = await RegisterBookUpload(uow, file_storage).execute(
        owner_user_id=uuid4(),
        title="Catalog Book",
        storage_key="assets/new/book.pdf",
        sha256="a" * 64,
        file_size_bytes=42,
        original_filename="book.pdf",
    )

    assert result.asset.storage_key.value == "assets/new/book.pdf"
    assert result.book.primary_asset_id == result.asset.id
    assert result.library_item.book_id == result.book.id
    assert result.stranded_storage_key is None
    assert result.stranded_storage_deleted is False
    book_asset_repo.save.assert_awaited_once()
    book_repo.save.assert_awaited_once()
    library_item_repo.save.assert_awaited_once()
    file_storage.delete.assert_not_awaited()
    mock_task.delay.assert_called_once_with(str(result.asset.id.value))


async def test_register_book_upload_cleans_up_duplicate_staged_blob_when_possible(
    uow, book_asset_repo, file_storage
):
    existing = _existing_asset(storage_key="assets/canonical/book.pdf")
    book_asset_repo.get_by_sha256.return_value = existing

    result = await RegisterBookUpload(uow, file_storage).execute(
        owner_user_id=uuid4(),
        title="Catalog Book",
        storage_key="assets/staged/book.pdf",
        sha256="b" * 64,
        file_size_bytes=42,
        original_filename="book.pdf",
    )

    assert result.asset is existing
    assert result.stranded_storage_key == "assets/staged/book.pdf"
    assert result.stranded_storage_deleted is True
    file_storage.delete.assert_awaited_once_with(storage_key="assets/staged/book.pdf")


async def test_register_book_upload_returns_cleanup_signal_without_storage(
    uow, book_asset_repo
):
    existing = _existing_asset(storage_key="assets/canonical/book.pdf")
    book_asset_repo.get_by_sha256.return_value = existing

    result = await RegisterBookUpload(uow).execute(
        owner_user_id=uuid4(),
        title="Catalog Book",
        storage_key="assets/staged/book.pdf",
        sha256="b" * 64,
        file_size_bytes=42,
        original_filename="book.pdf",
    )

    assert result.asset is existing
    assert result.stranded_storage_key == "assets/staged/book.pdf"
    assert result.stranded_storage_deleted is False
