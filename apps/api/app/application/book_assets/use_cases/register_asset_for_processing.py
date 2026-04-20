from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, cast
from uuid import UUID  # noqa: TC003

from sqlalchemy.exc import IntegrityError

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
)

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork


class _AssetProcessingTask(Protocol):
    def delay(self, asset_id: str) -> object: ...


@dataclass(frozen=True, slots=True)
class AssetRegistration:
    """Primitives describing an asset blob that has been placed in storage.

    `storage_key` identifies the logical location of the already-stored
    blob (the caller is responsible for putting bytes there before
    invoking the service). Dedup happens on `sha256`.

    Callers that need the asset row's id to align with the storage path
    can pass `asset_id` explicitly; otherwise a fresh one is generated.
    """

    sha256: str
    storage_key: str
    file_size_bytes: int
    original_filename: str
    mime_type: str = "application/pdf"
    storage_backend: str = StorageBackend.LOCAL.value
    asset_format: str = BookAssetFormat.PDF.value
    created_by_user_id: UUID | None = None
    asset_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class AssetRegistrationResult:
    asset: BookAsset
    created: bool
    needs_processing: bool


class RegisterAssetForProcessing:
    """Canonical seam for registering an asset and enqueuing processing.

    Every ingestion source — personal upload, pre-stored
    `RegisterBookUpload`, and the merchant ingestion flow that N1+ will
    build — goes through this service. Changes to worker orchestration,
    dedup rules, or state transitions land in one place.

    Dedup: if an asset with the same `sha256` already exists, it is
    returned unchanged. `needs_processing` reflects whether the caller
    should enqueue after commit — READY assets are skipped, any other
    state (pending/processing/error) is re-enqueued, relying on the
    R3.3 worker's idempotent entry point to resume or retry safely.

    Transaction contract: `execute` persists via the unit of work but
    does NOT commit — callers typically compose with Book and
    LibraryItem in the same transaction. It *does* flush the asset
    insert so sha256 uniqueness conflicts surface before callers stage
    additional rows. After committing, call `enqueue_processing()`
    with the returned asset id.
    """

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self, registration: AssetRegistration
    ) -> AssetRegistrationResult:
        sha256 = Sha256(registration.sha256)
        existing = await self._uow.book_assets.get_by_sha256(sha256)
        if existing is not None:
            return AssetRegistrationResult(
                asset=existing,
                created=False,
                needs_processing=(
                    existing.processing_status is not ProcessingStatus.READY
                ),
            )

        asset = BookAsset(
            id=(
                BookAssetId(registration.asset_id)
                if registration.asset_id is not None
                else BookAssetId.generate()
            ),
            sha256=Sha256(registration.sha256),
            format=BookAssetFormat(registration.asset_format),
            mime_type=MimeType(registration.mime_type),
            file_size_bytes=FileSizeBytes(registration.file_size_bytes),
            storage_backend=StorageBackend(registration.storage_backend),
            storage_key=StorageKey(registration.storage_key),
            original_filename=OriginalFilename(registration.original_filename),
            created_by_user_id=(
                UserId(registration.created_by_user_id)
                if registration.created_by_user_id is not None
                else None
            ),
        )
        await self._uow.book_assets.save(asset)
        try:
            await self._uow.flush()
        except IntegrityError:
            # Another transaction won the same-sha256 race. Roll back the
            # failed insert and re-read the canonical asset so callers can
            # continue with dedup semantics instead of a raw DB error.
            await self._uow.rollback()
            existing = await self._uow.book_assets.get_by_sha256(sha256)
            if existing is None:
                raise
            return AssetRegistrationResult(
                asset=existing,
                created=False,
                needs_processing=(
                    existing.processing_status is not ProcessingStatus.READY
                ),
            )
        return AssetRegistrationResult(
            asset=asset, created=True, needs_processing=True
        )

    @staticmethod
    def enqueue_processing(asset_id: BookAssetId) -> None:
        from app.workers.task import process_book_asset_task

        cast("_AssetProcessingTask", process_book_asset_task).delay(
            str(asset_id.value),
        )
