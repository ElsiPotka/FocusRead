from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Final, cast

from app.domain.book_asset.value_objects import BookAssetId, ProcessingStatus
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
BookStatus = ProcessingStatus


class Book:
    """Canonical catalog book.

    Owns identity, discoverable metadata, and the pointer to its primary
    `BookAsset`. It does NOT own the file, the processing lifecycle, or any
    per-user reader state — those belong to `BookAsset` and `LibraryItem`
    respectively.
    """

    def __init__(
        self,
        *,
        id: BookId,
        primary_asset_id: BookAssetId | None = None,
        title: BookTitle,
        created_by_user_id: UserId | None = None,
        owner_user_id: UserId | None = None,
        source_filename: BookSourceFilename | None = None,
        file_path: BookFilePath | None = None,
        subtitle: BookSubtitle | None = None,
        document_type: BookDocumentType = BookDocumentType.BOOK,
        description: BookDescription | None = None,
        language: BookLanguage | None = None,
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
        now = datetime.now(UTC)
        if (
            created_by_user_id is not None
            and owner_user_id is not None
            and created_by_user_id != owner_user_id
        ):
            raise ValueError(
                "created_by_user_id and owner_user_id must match when both are set."
            )
        self._id = id
        self._primary_asset_id = primary_asset_id or BookAssetId.generate()
        self._title = title
        self._created_by_user_id = created_by_user_id or owner_user_id
        self._source_filename = source_filename
        self._file_path = file_path
        self._subtitle = subtitle
        self._document_type = document_type
        self._description = description
        self._language = language
        self._cover_image_path = cover_image_path
        self._publisher = publisher
        self._published_year = published_year
        self._page_count = page_count
        self._word_count = word_count
        self._total_chunks = total_chunks
        self._has_images = has_images
        self._toc_extracted = toc_extracted
        self._status = status
        self._processing_error = processing_error
        self._created_at = created_at or now
        self._updated_at = updated_at or now

    @classmethod
    def create(
        cls,
        *,
        primary_asset_id: BookAssetId | None = None,
        title: BookTitle,
        created_by_user_id: UserId | None = None,
        owner_user_id: UserId | None = None,
        source_filename: BookSourceFilename | None = None,
        file_path: BookFilePath | None = None,
        subtitle: BookSubtitle | None = None,
        document_type: BookDocumentType = BookDocumentType.BOOK,
        description: BookDescription | None = None,
        language: BookLanguage | None = None,
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
    ) -> Book:
        if (
            created_by_user_id is not None
            and owner_user_id is not None
            and created_by_user_id != owner_user_id
        ):
            raise ValueError(
                "created_by_user_id and owner_user_id must match when both are set."
            )
        return cls(
            id=BookId.generate(),
            primary_asset_id=primary_asset_id or BookAssetId.generate(),
            title=title,
            created_by_user_id=created_by_user_id or owner_user_id,
            source_filename=source_filename,
            file_path=file_path,
            subtitle=subtitle,
            document_type=document_type,
            description=description,
            language=language,
            cover_image_path=cover_image_path,
            publisher=publisher,
            published_year=published_year,
            page_count=page_count,
            word_count=word_count,
            total_chunks=total_chunks,
            has_images=has_images,
            toc_extracted=toc_extracted,
            status=status,
            processing_error=processing_error,
        )

    @property
    def id(self) -> BookId:
        return self._id

    @property
    def primary_asset_id(self) -> BookAssetId:
        return self._primary_asset_id

    @property
    def title(self) -> BookTitle:
        return self._title

    @property
    def created_by_user_id(self) -> UserId | None:
        return self._created_by_user_id

    @property
    def owner_user_id(self) -> UserId:
        if self._created_by_user_id is None:
            raise ValueError("Book has no owner_user_id.")
        return self._created_by_user_id

    @property
    def source_filename(self) -> BookSourceFilename | None:
        return self._source_filename

    @property
    def file_path(self) -> BookFilePath:
        if self._file_path is None:
            raise ValueError("Book has no file_path.")
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
        source_filename: BookSourceFilename | None | object = _UNSET,
        file_path: BookFilePath | None | object = _UNSET,
        subtitle: BookSubtitle | None | object = _UNSET,
        document_type: BookDocumentType | object = _UNSET,
        description: BookDescription | None | object = _UNSET,
        language: BookLanguage | None | object = _UNSET,
        cover_image_path: BookCoverImagePath | None | object = _UNSET,
        publisher: BookPublisher | None | object = _UNSET,
        published_year: BookPublishedYear | None | object = _UNSET,
        page_count: BookPageCount | None | object = _UNSET,
        word_count: BookWordCount | None | object = _UNSET,
        total_chunks: BookTotalChunks | None | object = _UNSET,
        has_images: bool | object = _UNSET,
        toc_extracted: bool | object = _UNSET,
    ) -> None:
        if title is not _UNSET:
            self._title = cast("BookTitle", title)
        if source_filename is not _UNSET:
            self._source_filename = cast("BookSourceFilename | None", source_filename)
        if file_path is not _UNSET:
            self._file_path = cast("BookFilePath | None", file_path)
        if subtitle is not _UNSET:
            self._subtitle = cast("BookSubtitle | None", subtitle)
        if document_type is not _UNSET:
            self._document_type = cast("BookDocumentType", document_type)
        if description is not _UNSET:
            self._description = cast("BookDescription | None", description)
        if language is not _UNSET:
            self._language = cast("BookLanguage | None", language)
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
        if self._status in (BookStatus.PROCESSING, BookStatus.READY):
            return
        self._status = BookStatus.PROCESSING
        self._processing_error = None
        self._updated_at = datetime.now(UTC)

    def mark_ready(self) -> None:
        if self._status is BookStatus.READY:
            return
        self._status = BookStatus.READY
        self._processing_error = None
        self._updated_at = datetime.now(UTC)

    def mark_error(self, error: BookProcessingError | None = None) -> None:
        self._status = BookStatus.ERROR
        self._processing_error = error
        self._updated_at = datetime.now(UTC)

    def update_processing_details(
        self,
        *,
        page_count: BookPageCount | None | object = _UNSET,
        word_count: BookWordCount | None | object = _UNSET,
        total_chunks: BookTotalChunks | None | object = _UNSET,
        has_images: bool | object = _UNSET,
        toc_extracted: bool | object = _UNSET,
    ) -> None:
        self.update_metadata(
            page_count=page_count,
            word_count=word_count,
            total_chunks=total_chunks,
            has_images=has_images,
            toc_extracted=toc_extracted,
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Book) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
