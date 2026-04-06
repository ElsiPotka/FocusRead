from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.domain.auth.value_objects import UserId
from app.domain.books.entities import Book, BookStatus
from app.domain.books.value_objects import (
    BookDescription,
    BookDocumentType,
    BookFilePath,
    BookProcessingError,
    BookSourceFilename,
    BookSubtitle,
    BookTitle,
)


class TestBook:
    def test_create_sets_expected_defaults(self):
        owner_user_id = UserId(uuid4())

        book = Book.create(
            owner_user_id=owner_user_id,
            title=BookTitle("Deep Work"),
            file_path=BookFilePath("/tmp/deep-work.pdf"),
            source_filename=BookSourceFilename("deep-work.pdf"),
        )

        assert book.owner_user_id == owner_user_id
        assert book.title.value == "Deep Work"
        assert book.source_filename is not None
        assert book.source_filename.value == "deep-work.pdf"
        assert book.document_type is BookDocumentType.BOOK
        assert book.status is BookStatus.PENDING
        assert book.processing_error is None
        assert isinstance(book.created_at, datetime)
        assert isinstance(book.updated_at, datetime)

    def test_update_metadata_replaces_and_clears_optional_fields(self):
        book = Book.create(
            owner_user_id=UserId(uuid4()),
            title=BookTitle("Original"),
            file_path=BookFilePath("/tmp/original.pdf"),
        )
        before = book.updated_at

        book.update_metadata(
            title=BookTitle("Updated"),
            subtitle=BookSubtitle("A subtitle"),
            description=BookDescription("A concise description"),
        )
        book.update_metadata(
            subtitle=None,
            description=None,
            document_type=BookDocumentType.PAPER,
        )

        assert book.title.value == "Updated"
        assert book.subtitle is None
        assert book.description is None
        assert book.document_type is BookDocumentType.PAPER
        assert book.updated_at >= before

    def test_mark_error_stores_processing_error(self):
        book = Book.create(
            owner_user_id=UserId(uuid4()),
            title=BookTitle("Broken"),
            file_path=BookFilePath("/tmp/broken.pdf"),
        )

        book.mark_error(BookProcessingError("Parser failed on page 12"))

        assert book.status is BookStatus.ERROR
        assert book.processing_error is not None
        assert book.processing_error.value == "Parser failed on page 12"
