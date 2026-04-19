from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Final, cast

from app.domain.book_asset.errors import InvalidBookAssetStateError
from app.domain.book_asset.value_objects import (
    BookAssetFormat,
    BookAssetId,
    FileSizeBytes,
    MimeType,
    OriginalFilename,
    PageCount,
    ProcessingError,
    ProcessingStatus,
    Sha256,
    StorageBackend,
    StorageKey,
    TotalChunks,
    WordCount,
)

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId

_UNSET: Final = object()


class BookAsset:
    def __init__(
        self,
        *,
        id: BookAssetId,
        sha256: Sha256,
        format: BookAssetFormat,
        mime_type: MimeType,
        file_size_bytes: FileSizeBytes,
        storage_backend: StorageBackend,
        storage_key: StorageKey,
        original_filename: OriginalFilename,
        created_by_user_id: UserId | None,
        processing_status: ProcessingStatus = ProcessingStatus.PENDING,
        processing_error: ProcessingError | None = None,
        page_count: PageCount | None = None,
        word_count: WordCount | None = None,
        total_chunks: TotalChunks | None = None,
        has_images: bool = False,
        toc_extracted: bool = False,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self._id: BookAssetId = id
        self._sha256: Sha256 = sha256
        self._format: BookAssetFormat = format
        self._mime_type: MimeType = mime_type
        self._file_size_bytes: FileSizeBytes = file_size_bytes
        self._storage_backend: StorageBackend = storage_backend
        self._storage_key: StorageKey = storage_key
        self._original_filename: OriginalFilename = original_filename
        self._created_by_user_id: UserId | None = created_by_user_id
        self._processing_status: ProcessingStatus = processing_status
        self._processing_error: ProcessingError | None = processing_error
        self._page_count: PageCount | None = page_count
        self._word_count: WordCount | None = word_count
        self._total_chunks: TotalChunks | None = total_chunks
        self._has_images: bool = has_images
        self._toc_extracted: bool = toc_extracted
        self._created_at: datetime = created_at or datetime.now(UTC)
        self._updated_at: datetime = updated_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        *,
        sha256: Sha256,
        mime_type: MimeType,
        file_size_bytes: FileSizeBytes,
        storage_backend: StorageBackend,
        storage_key: StorageKey,
        original_filename: OriginalFilename,
        created_by_user_id: UserId | None,
        format: BookAssetFormat = BookAssetFormat.PDF,
    ) -> BookAsset:
        return cls(
            id=BookAssetId.generate(),
            sha256=sha256,
            format=format,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            storage_backend=storage_backend,
            storage_key=storage_key,
            original_filename=original_filename,
            created_by_user_id=created_by_user_id,
            processing_status=ProcessingStatus.PENDING,
        )

    @property
    def id(self) -> BookAssetId:
        return self._id

    @property
    def sha256(self) -> Sha256:
        return self._sha256

    @property
    def format(self) -> BookAssetFormat:
        return self._format

    @property
    def mime_type(self) -> MimeType:
        return self._mime_type

    @property
    def file_size_bytes(self) -> FileSizeBytes:
        return self._file_size_bytes

    @property
    def storage_backend(self) -> StorageBackend:
        return self._storage_backend

    @property
    def storage_key(self) -> StorageKey:
        return self._storage_key

    @property
    def original_filename(self) -> OriginalFilename:
        return self._original_filename

    @property
    def created_by_user_id(self) -> UserId | None:
        return self._created_by_user_id

    @property
    def processing_status(self) -> ProcessingStatus:
        return self._processing_status

    @property
    def processing_error(self) -> ProcessingError | None:
        return self._processing_error

    @property
    def page_count(self) -> PageCount | None:
        return self._page_count

    @property
    def word_count(self) -> WordCount | None:
        return self._word_count

    @property
    def total_chunks(self) -> TotalChunks | None:
        return self._total_chunks

    @property
    def has_images(self) -> bool:
        return self._has_images

    @property
    def toc_extracted(self) -> bool:
        return self._toc_extracted

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def mark_processing(self) -> None:
        if self._processing_status is ProcessingStatus.READY:
            return
        if self._processing_status is ProcessingStatus.PROCESSING:
            return
        if self._processing_status not in (
            ProcessingStatus.PENDING,
            ProcessingStatus.ERROR,
        ):
            raise InvalidBookAssetStateError(
                "Only pending or errored assets can (re-)enter processing."
            )
        self._processing_status = ProcessingStatus.PROCESSING
        self._processing_error = None
        self._updated_at = datetime.now(UTC)

    def mark_ready(self) -> None:
        if self._processing_status is ProcessingStatus.READY:
            return
        if self._processing_status is not ProcessingStatus.PROCESSING:
            raise InvalidBookAssetStateError("Only processing assets can become ready.")
        self._processing_status = ProcessingStatus.READY
        self._processing_error = None
        self._updated_at = datetime.now(UTC)

    def mark_error(self, error: ProcessingError | None = None) -> None:
        self._processing_status = ProcessingStatus.ERROR
        self._processing_error = error
        self._updated_at = datetime.now(UTC)

    def update_processing_details(
        self,
        *,
        page_count: PageCount | None | object = _UNSET,
        word_count: WordCount | None | object = _UNSET,
        total_chunks: TotalChunks | None | object = _UNSET,
        has_images: bool | object = _UNSET,
        toc_extracted: bool | object = _UNSET,
    ) -> None:
        if page_count is not _UNSET:
            self._page_count = cast("PageCount | None", page_count)
        if word_count is not _UNSET:
            self._word_count = cast("WordCount | None", word_count)
        if total_chunks is not _UNSET:
            self._total_chunks = cast("TotalChunks | None", total_chunks)
        if has_images is not _UNSET:
            self._has_images = cast("bool", has_images)
        if toc_extracted is not _UNSET:
            self._toc_extracted = cast("bool", toc_extracted)
        self._updated_at = datetime.now(UTC)
