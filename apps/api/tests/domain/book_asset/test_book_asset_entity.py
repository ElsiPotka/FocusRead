from __future__ import annotations

from uuid import uuid4

import pytest

from app.domain.auth.value_objects import UserId
from app.domain.book_asset.entities import BookAsset
from app.domain.book_asset.errors import InvalidBookAssetStateError
from app.domain.book_asset.value_objects import (
    BookAssetFormat,
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


def _make_asset(**overrides) -> BookAsset:
    defaults = {
        "sha256": Sha256("a" * 64),
        "mime_type": MimeType("application/pdf"),
        "file_size_bytes": FileSizeBytes(1024),
        "storage_backend": StorageBackend.LOCAL,
        "storage_key": StorageKey("books/sha256/aa/aa/" + ("a" * 64) + ".pdf"),
        "original_filename": OriginalFilename("book.pdf"),
        "created_by_user_id": UserId(uuid4()),
        "format": BookAssetFormat.PDF,
    }
    defaults.update(overrides)
    return BookAsset.create(**defaults)


class TestBookAssetCreation:
    def test_starts_pending(self):
        asset = _make_asset()

        assert asset.processing_status is ProcessingStatus.PENDING
        assert asset.processing_error is None
        assert asset.page_count is None
        assert asset.word_count is None
        assert asset.total_chunks is None
        assert asset.has_images is False
        assert asset.toc_extracted is False

    def test_generates_id_and_timestamps(self):
        asset = _make_asset()

        assert asset.id is not None
        assert asset.created_at is not None
        assert asset.updated_at is not None


class TestBookAssetStateTransitions:
    def test_pending_to_processing(self):
        asset = _make_asset()

        asset.mark_processing()

        assert asset.processing_status is ProcessingStatus.PROCESSING
        assert asset.processing_error is None

    def test_processing_to_ready(self):
        asset = _make_asset()
        asset.mark_processing()

        asset.mark_ready()

        assert asset.processing_status is ProcessingStatus.READY

    def test_error_from_any_state(self):
        asset = _make_asset()
        err = ProcessingError("bad pdf")

        asset.mark_error(err)

        assert asset.processing_status is ProcessingStatus.ERROR
        assert asset.processing_error == err

    def test_errored_asset_can_re_enter_processing(self):
        asset = _make_asset()
        asset.mark_error(ProcessingError("bad pdf"))

        asset.mark_processing()

        assert asset.processing_status is ProcessingStatus.PROCESSING
        assert asset.processing_error is None

    def test_mark_processing_is_idempotent_on_processing(self):
        asset = _make_asset()
        asset.mark_processing()

        asset.mark_processing()

        assert asset.processing_status is ProcessingStatus.PROCESSING

    def test_mark_processing_is_noop_on_ready(self):
        """Supports worker idempotency: retrying process on a ready asset is a no-op."""
        asset = _make_asset()
        asset.mark_processing()
        asset.mark_ready()

        asset.mark_processing()

        assert asset.processing_status is ProcessingStatus.READY

    def test_mark_ready_is_idempotent_on_ready(self):
        asset = _make_asset()
        asset.mark_processing()
        asset.mark_ready()

        asset.mark_ready()

        assert asset.processing_status is ProcessingStatus.READY

    def test_mark_ready_from_pending_is_invalid(self):
        asset = _make_asset()

        with pytest.raises(InvalidBookAssetStateError):
            asset.mark_ready()

    def test_mark_ready_from_error_is_invalid(self):
        asset = _make_asset()
        asset.mark_error(ProcessingError("oops"))

        with pytest.raises(InvalidBookAssetStateError):
            asset.mark_ready()


class TestUpdateProcessingDetails:
    def test_sets_counts_and_flags(self):
        asset = _make_asset()

        asset.update_processing_details(
            page_count=PageCount(200),
            word_count=WordCount(50_000),
            total_chunks=TotalChunks(80),
            has_images=True,
            toc_extracted=True,
        )

        assert asset.page_count == PageCount(200)
        assert asset.word_count == WordCount(50_000)
        assert asset.total_chunks == TotalChunks(80)
        assert asset.has_images is True
        assert asset.toc_extracted is True

    def test_unset_fields_are_preserved(self):
        asset = _make_asset()
        asset.update_processing_details(page_count=PageCount(100))

        asset.update_processing_details(word_count=WordCount(20_000))

        assert asset.page_count == PageCount(100)
        assert asset.word_count == WordCount(20_000)
