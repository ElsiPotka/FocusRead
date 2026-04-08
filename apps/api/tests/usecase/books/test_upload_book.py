from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.application.books.use_cases.upload_book import UploadBook
from app.application.common.unit_of_work import AbstractUnitOfWork
from app.domain.books.entities import BookStatus
from app.domain.books.repositories import BookRepository
from app.infrastructure.storage.file_storage import FileStorage


@pytest.fixture
def book_repo():
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def chunk_repo():
    return AsyncMock()


@pytest.fixture
def uow(book_repo, chunk_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.books = book_repo
    mock.book_chunks = chunk_repo
    return mock


@pytest.fixture
def file_storage():
    storage = AsyncMock(spec=FileStorage)
    storage.save_upload.return_value = "/storage/uploads/test/book.pdf"
    return storage


@patch("app.workers.task.process_book_task")
async def test_upload_creates_pending_book(mock_task, uow, book_repo, file_storage):
    owner_id = uuid4()

    book = await UploadBook(uow, file_storage).execute(
        owner_user_id=owner_id,
        title="Test Book",
        source_filename="test.pdf",
        file_content=b"%PDF-1.4 fake content",
    )

    assert book.status is BookStatus.PENDING
    assert book.title.value == "Test Book"
    assert book.owner_user_id.value == owner_id
    book_repo.save.assert_awaited_once()
    uow.commit.assert_awaited_once()


@patch("app.workers.task.process_book_task")
async def test_upload_saves_file_via_storage(mock_task, uow, file_storage):
    owner_id = uuid4()

    await UploadBook(uow, file_storage).execute(
        owner_user_id=owner_id,
        title="Test Book",
        source_filename="mybook.pdf",
        file_content=b"%PDF-1.4 content",
    )

    file_storage.save_upload.assert_awaited_once()
    call_kwargs = file_storage.save_upload.call_args.kwargs
    assert call_kwargs["file_content"] == b"%PDF-1.4 content"
    assert "mybook.pdf" in call_kwargs["destination"]


@patch("app.workers.task.process_book_task")
async def test_upload_enqueues_celery_task(mock_task, uow, file_storage):
    book = await UploadBook(uow, file_storage).execute(
        owner_user_id=uuid4(),
        title="Test Book",
        source_filename="test.pdf",
        file_content=b"%PDF-1.4 content",
    )

    mock_task.delay.assert_called_once_with(str(book.id.value))


@patch("app.workers.task.process_book_task")
async def test_upload_records_source_filename(mock_task, uow, file_storage):
    book = await UploadBook(uow, file_storage).execute(
        owner_user_id=uuid4(),
        title="My PDF",
        source_filename="important-doc.pdf",
        file_content=b"%PDF content",
    )

    assert book.source_filename is not None
    assert book.source_filename.value == "important-doc.pdf"


@patch("app.workers.task.process_book_task")
async def test_upload_uses_custom_document_type(mock_task, uow, file_storage):
    book = await UploadBook(uow, file_storage).execute(
        owner_user_id=uuid4(),
        title="Research Paper",
        source_filename="paper.pdf",
        file_content=b"%PDF content",
        document_type="paper",
    )

    assert book.document_type.value == "paper"
