from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.application.books.use_cases.upload_book import UploadBook
from app.application.common.unit_of_work import AbstractUnitOfWork
from app.domain.book_asset.repositories import BookAssetRepository
from app.domain.book_asset.value_objects import ProcessingStatus, StorageBackend
from app.domain.books.repositories import BookRepository
from app.domain.library_item.repositories import LibraryItemRepository
from app.domain.library_item.value_objects import AccessStatus, LibrarySourceKind
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
    storage.store.return_value = None
    return storage


@patch("app.workers.task.process_book_asset_task")
async def test_upload_creates_pending_asset_book_and_library_item(
    mock_task, uow, book_repo, book_asset_repo, library_item_repo, file_storage
):
    owner_id = uuid4()

    result = await UploadBook(uow, file_storage).execute(
        owner_user_id=owner_id,
        title="Test Book",
        source_filename="test.pdf",
        file_content=b"%PDF-1.4 fake content",
    )

    assert result.asset.processing_status is ProcessingStatus.PENDING
    assert result.asset.created_by_user_id is not None
    assert result.asset.created_by_user_id.value == owner_id
    assert result.asset.storage_backend is StorageBackend.LOCAL

    assert result.book.title.value == "Test Book"
    assert result.book.primary_asset_id == result.asset.id
    assert result.book.created_by_user_id is not None
    assert result.book.created_by_user_id.value == owner_id

    assert result.library_item.user_id.value == owner_id
    assert result.library_item.book_id == result.book.id
    assert result.library_item.source_kind is LibrarySourceKind.UPLOAD
    assert result.library_item.access_status is AccessStatus.ACTIVE

    book_asset_repo.save.assert_awaited_once()
    book_repo.save.assert_awaited_once()
    library_item_repo.save.assert_awaited_once()
    uow.commit.assert_awaited_once()


@patch("app.workers.task.process_book_asset_task")
async def test_upload_saves_file_via_storage_with_asset_aware_key(
    mock_task, uow, file_storage
):
    owner_id = uuid4()

    result = await UploadBook(uow, file_storage).execute(
        owner_user_id=owner_id,
        title="Test Book",
        source_filename="mybook.pdf",
        file_content=b"%PDF-1.4 content",
    )

    file_storage.store.assert_awaited_once()
    call_kwargs = file_storage.store.call_args.kwargs
    assert call_kwargs["content"] == b"%PDF-1.4 content"
    assert str(result.asset.id.value) in call_kwargs["storage_key"]
    assert call_kwargs["storage_key"].endswith("mybook.pdf")
    assert result.asset.storage_key.value == call_kwargs["storage_key"]


@patch("app.workers.task.process_book_asset_task")
async def test_upload_enqueues_celery_task(mock_task, uow, file_storage):
    result = await UploadBook(uow, file_storage).execute(
        owner_user_id=uuid4(),
        title="Test Book",
        source_filename="test.pdf",
        file_content=b"%PDF-1.4 content",
    )

    mock_task.delay.assert_called_once_with(str(result.asset.id.value))


@patch("app.workers.task.process_book_asset_task")
async def test_upload_records_source_filename(mock_task, uow, file_storage):
    result = await UploadBook(uow, file_storage).execute(
        owner_user_id=uuid4(),
        title="My PDF",
        source_filename="important-doc.pdf",
        file_content=b"%PDF content",
    )

    assert result.book.source_filename is not None
    assert result.book.source_filename.value == "important-doc.pdf"
    assert result.asset.original_filename.value == "important-doc.pdf"


@patch("app.workers.task.process_book_asset_task")
async def test_upload_uses_custom_document_type(mock_task, uow, file_storage):
    result = await UploadBook(uow, file_storage).execute(
        owner_user_id=uuid4(),
        title="Research Paper",
        source_filename="paper.pdf",
        file_content=b"%PDF content",
        document_type="paper",
    )

    assert result.book.document_type.value == "paper"


@patch("app.workers.task.process_book_asset_task")
async def test_upload_computes_sha256_and_size_on_asset(mock_task, uow, file_storage):
    content = b"%PDF-1.4 deterministic payload"

    result = await UploadBook(uow, file_storage).execute(
        owner_user_id=uuid4(),
        title="Hashed",
        source_filename="h.pdf",
        file_content=content,
    )

    import hashlib

    assert result.asset.sha256.value == hashlib.sha256(content).hexdigest()
    assert result.asset.file_size_bytes.value == len(content)
