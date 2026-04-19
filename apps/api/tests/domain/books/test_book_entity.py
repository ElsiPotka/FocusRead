from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.domain.auth.value_objects import UserId
from app.domain.book_asset.value_objects import BookAssetId
from app.domain.books.entities import Book
from app.domain.books.value_objects import (
    BookCoverImagePath,
    BookDescription,
    BookDocumentType,
    BookLanguage,
    BookPublishedYear,
    BookPublisher,
    BookSubtitle,
    BookTitle,
)


def _make_book(
    *,
    primary_asset_id: BookAssetId | None = None,
    title: BookTitle | None = None,
    created_by_user_id: UserId | None = None,
) -> Book:
    return Book.create(
        primary_asset_id=primary_asset_id or BookAssetId(uuid4()),
        title=title or BookTitle("Deep Work"),
        created_by_user_id=created_by_user_id,
    )


class TestBookCreation:
    def test_create_sets_expected_defaults(self):
        asset_id = BookAssetId(uuid4())

        book = Book.create(
            primary_asset_id=asset_id,
            title=BookTitle("Deep Work"),
        )

        assert book.id is not None
        assert book.primary_asset_id == asset_id
        assert book.title.value == "Deep Work"
        assert book.document_type is BookDocumentType.BOOK
        assert book.subtitle is None
        assert book.description is None
        assert book.language is None
        assert book.cover_image_path is None
        assert book.publisher is None
        assert book.published_year is None
        assert book.created_by_user_id is None
        assert isinstance(book.created_at, datetime)
        assert isinstance(book.updated_at, datetime)

    def test_create_captures_attribution(self):
        user_id = UserId(uuid4())

        book = _make_book(created_by_user_id=user_id)

        assert book.created_by_user_id == user_id


class TestUpdateMetadata:
    def test_replaces_and_clears_optional_fields(self):
        book = _make_book(title=BookTitle("Original"))
        before = book.updated_at

        book.update_metadata(
            title=BookTitle("Updated"),
            subtitle=BookSubtitle("A subtitle"),
            description=BookDescription("A concise description"),
            language=BookLanguage("en"),
            publisher=BookPublisher("ACME Press"),
            published_year=BookPublishedYear(2024),
            cover_image_path=BookCoverImagePath("/covers/x.jpg"),
            document_type=BookDocumentType.PAPER,
        )

        assert book.title.value == "Updated"
        assert book.subtitle is not None
        assert book.subtitle.value == "A subtitle"
        assert book.description is not None
        assert book.description.value == "A concise description"
        assert book.language is not None
        assert book.language.value == "en"
        assert book.publisher is not None
        assert book.publisher.value == "ACME Press"
        assert book.published_year is not None
        assert book.published_year.value == 2024
        assert book.cover_image_path is not None
        assert book.cover_image_path.value == "/covers/x.jpg"
        assert book.document_type is BookDocumentType.PAPER
        assert book.updated_at >= before

    def test_unset_preserves_existing(self):
        book = _make_book()
        book.update_metadata(
            subtitle=BookSubtitle("Keep me"),
            publisher=BookPublisher("Keep me too"),
        )

        book.update_metadata(description=BookDescription("new"))

        assert book.subtitle is not None
        assert book.subtitle.value == "Keep me"
        assert book.publisher is not None
        assert book.publisher.value == "Keep me too"
        assert book.description is not None
        assert book.description.value == "new"

    def test_can_clear_optional_fields_to_none(self):
        book = _make_book()
        book.update_metadata(
            subtitle=BookSubtitle("To be cleared"),
            publisher=BookPublisher("Also cleared"),
        )

        book.update_metadata(subtitle=None, publisher=None)

        assert book.subtitle is None
        assert book.publisher is None


class TestEquality:
    def test_equal_by_id(self):
        book = _make_book()
        other_view = Book(
            id=book.id,
            primary_asset_id=BookAssetId(uuid4()),
            title=BookTitle("Something else"),
        )

        assert book == other_view
        assert hash(book) == hash(other_view)
