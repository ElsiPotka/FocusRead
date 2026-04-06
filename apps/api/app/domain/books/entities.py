from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Final, cast

from app.domain.books.errors import InvalidBookStateError
from app.domain.books.value_objects import (
    BookCoverImagePath,
    BookDescription,
    BookDocumentType,
    BookFilePath,
    BookId,
    BookLanguage,
    BookPageCount,
    BookProcessingError,
    BookPublishedYear,
    BookPublisher,
    BookSourceFilename,
    BookSubtitle,
    BookTitle,
    BookTotalChunks,
    BookWordCount,
)

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId

_UNSET: Final = object()


class BookStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class Book:
    def __init__(
        self,
        *,
        id: BookId,
        owner_user_id: UserId,
        title: BookTitle,
        file_path: BookFilePath,
        subtitle: BookSubtitle | None = None,
        document_type: BookDocumentType = BookDocumentType.BOOK,
        description: BookDescription | None = None,
        language: BookLanguage | None = None,
        source_filename: BookSourceFilename | None = None,
        cover_image_path: BookCoverImagePath | None = None,
        publisher: BookPublisher | None = None,
        published_year: BookPublishedYear | None = None,
        page_count: BookPageCount | None = None,
        word_count: BookWordCount | None = None,
        total_chunks: BookTotalChunks | None = None,
        has_images: bool = False,
        toc_extracted: bool = False,
        status: BookStatus = BookStatus.PENDING,
        processing_error: BookProcessingError | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self._id: BookId = id
        self._owner_user_id: UserId = owner_user_id
        self._title: BookTitle = title
        self._file_path: BookFilePath = file_path
        self._subtitle: BookSubtitle | None = subtitle
        self._document_type: BookDocumentType = document_type
        self._description: BookDescription | None = description
        self._language: BookLanguage | None = language
        self._source_filename: BookSourceFilename | None = source_filename
        self._cover_image_path: BookCoverImagePath | None = cover_image_path
        self._publisher: BookPublisher | None = publisher
        self._published_year: BookPublishedYear | None = published_year
        self._page_count: BookPageCount | None = page_count
        self._word_count: BookWordCount | None = word_count
        self._total_chunks: BookTotalChunks | None = total_chunks
        self._has_images: bool = has_images
        self._toc_extracted: bool = toc_extracted
        self._status: BookStatus = status
        self._processing_error: BookProcessingError | None = processing_error
        self._created_at: datetime = created_at or datetime.now(UTC)
        self._updated_at: datetime = updated_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        *,
        owner_user_id: UserId,
        title: BookTitle,
        file_path: BookFilePath,
        source_filename: BookSourceFilename | None = None,
        document_type: BookDocumentType = BookDocumentType.BOOK,
    ) -> Book:
        return cls(
            id=BookId.generate(),
            owner_user_id=owner_user_id,
            title=title,
            file_path=file_path,
            source_filename=source_filename,
            document_type=document_type,
            status=BookStatus.PENDING,
        )

    @property
    def id(self) -> BookId:
        return self._id

    @property
    def owner_user_id(self) -> UserId:
        return self._owner_user_id

    @property
    def title(self) -> BookTitle:
        return self._title

    @property
    def file_path(self) -> BookFilePath:
        return self._file_path

    @property
    def subtitle(self) -> BookSubtitle | None:
        return self._subtitle

    @property
    def document_type(self) -> BookDocumentType:
        return self._document_type

    @property
    def description(self) -> BookDescription | None:
        return self._description

    @property
    def language(self) -> BookLanguage | None:
        return self._language

    @property
    def source_filename(self) -> BookSourceFilename | None:
        return self._source_filename

    @property
    def cover_image_path(self) -> BookCoverImagePath | None:
        return self._cover_image_path

    @property
    def publisher(self) -> BookPublisher | None:
        return self._publisher

    @property
    def published_year(self) -> BookPublishedYear | None:
        return self._published_year

    @property
    def page_count(self) -> BookPageCount | None:
        return self._page_count

    @property
    def word_count(self) -> BookWordCount | None:
        return self._word_count

    @property
    def total_chunks(self) -> BookTotalChunks | None:
        return self._total_chunks

    @property
    def has_images(self) -> bool:
        return self._has_images

    @property
    def toc_extracted(self) -> bool:
        return self._toc_extracted

    @property
    def status(self) -> BookStatus:
        return self._status

    @property
    def processing_error(self) -> BookProcessingError | None:
        return self._processing_error

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def update_metadata(
        self,
        *,
        title: BookTitle | object = _UNSET,
        subtitle: BookSubtitle | None | object = _UNSET,
        document_type: BookDocumentType | object = _UNSET,
        description: BookDescription | None | object = _UNSET,
        language: BookLanguage | None | object = _UNSET,
        source_filename: BookSourceFilename | None | object = _UNSET,
        cover_image_path: BookCoverImagePath | None | object = _UNSET,
        publisher: BookPublisher | None | object = _UNSET,
        published_year: BookPublishedYear | None | object = _UNSET,
        page_count: BookPageCount | None | object = _UNSET,
    ) -> None:
        if title is not _UNSET:
            self._title = cast("BookTitle", title)
        if subtitle is not _UNSET:
            self._subtitle = cast("BookSubtitle | None", subtitle)
        if document_type is not _UNSET:
            self._document_type = cast("BookDocumentType", document_type)
        if description is not _UNSET:
            self._description = cast("BookDescription | None", description)
        if language is not _UNSET:
            self._language = cast("BookLanguage | None", language)
        if source_filename is not _UNSET:
            self._source_filename = cast("BookSourceFilename | None", source_filename)
        if cover_image_path is not _UNSET:
            self._cover_image_path = cast(
                "BookCoverImagePath | None",
                cover_image_path,
            )
        if publisher is not _UNSET:
            self._publisher = cast("BookPublisher | None", publisher)
        if published_year is not _UNSET:
            self._published_year = cast("BookPublishedYear | None", published_year)
        if page_count is not _UNSET:
            self._page_count = cast("BookPageCount | None", page_count)
        self._updated_at = datetime.now(UTC)

    def update_processing_details(
        self,
        *,
        word_count: BookWordCount | None | object = _UNSET,
        total_chunks: BookTotalChunks | None | object = _UNSET,
        has_images: bool | object = _UNSET,
        toc_extracted: bool | object = _UNSET,
    ) -> None:
        if word_count is not _UNSET:
            self._word_count = cast("BookWordCount | None", word_count)
        if total_chunks is not _UNSET:
            self._total_chunks = cast("BookTotalChunks | None", total_chunks)
        if has_images is not _UNSET:
            self._has_images = cast("bool", has_images)
        if toc_extracted is not _UNSET:
            self._toc_extracted = cast("bool", toc_extracted)
        self._updated_at = datetime.now(UTC)

    def mark_processing(self) -> None:
        if self._status is not BookStatus.PENDING:
            raise InvalidBookStateError("Only pending books can start processing.")
        self._status = BookStatus.PROCESSING
        self._processing_error = None
        self._updated_at = datetime.now(UTC)

    def mark_ready(self) -> None:
        if self._status is not BookStatus.PROCESSING:
            raise InvalidBookStateError("Only processing books can become ready.")
        self._status = BookStatus.READY
        self._processing_error = None
        self._updated_at = datetime.now(UTC)

    def mark_error(self, error: BookProcessingError | None = None) -> None:
        self._status = BookStatus.ERROR
        self._processing_error = error
        self._updated_at = datetime.now(UTC)
