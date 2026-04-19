from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.domain.auth.value_objects import UserId
from app.domain.book_asset.entities import BookAsset
from app.domain.book_asset.repositories import BookAssetRepository
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
from app.infrastructure.persistence.models.book import BookModel
from app.infrastructure.persistence.models.book_asset import BookAssetModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.domain.books.value_objects import BookId


class SqlAlchemyBookAssetRepository(BookAssetRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, asset: BookAsset) -> None:
        model = await self.session.get(BookAssetModel, asset.id.value)
        if model is None:
            model = BookAssetModel(
                id=asset.id.value,
                sha256=asset.sha256.value,
                format=asset.format.value,
                mime_type=asset.mime_type.value,
                file_size_bytes=asset.file_size_bytes.value,
                storage_backend=asset.storage_backend.value,
                storage_key=asset.storage_key.value,
                original_filename=asset.original_filename.value,
                created_by_user_id=(
                    asset.created_by_user_id.value if asset.created_by_user_id else None
                ),
                processing_status=asset.processing_status.value,
                processing_error=(
                    asset.processing_error.value if asset.processing_error else None
                ),
                page_count=asset.page_count.value if asset.page_count else None,
                word_count=asset.word_count.value if asset.word_count else None,
                total_chunks=(asset.total_chunks.value if asset.total_chunks else None),
                has_images=asset.has_images,
                toc_extracted=asset.toc_extracted,
                created_at=asset.created_at,
                updated_at=asset.updated_at,
            )
            self.session.add(model)
            return

        model.sha256 = asset.sha256.value
        model.format = asset.format.value
        model.mime_type = asset.mime_type.value
        model.file_size_bytes = asset.file_size_bytes.value
        model.storage_backend = asset.storage_backend.value
        model.storage_key = asset.storage_key.value
        model.original_filename = asset.original_filename.value
        model.created_by_user_id = (
            asset.created_by_user_id.value if asset.created_by_user_id else None
        )
        model.processing_status = asset.processing_status.value
        model.processing_error = (
            asset.processing_error.value if asset.processing_error else None
        )
        model.page_count = asset.page_count.value if asset.page_count else None
        model.word_count = asset.word_count.value if asset.word_count else None
        model.total_chunks = asset.total_chunks.value if asset.total_chunks else None
        model.has_images = asset.has_images
        model.toc_extracted = asset.toc_extracted
        model.updated_at = asset.updated_at

    async def get(self, asset_id: BookAssetId) -> BookAsset | None:
        model = await self.session.get(BookAssetModel, asset_id.value)
        if model is None:
            return None
        return self._to_entity(model)

    async def get_by_sha256(self, sha256: Sha256) -> BookAsset | None:
        stmt = select(BookAssetModel).where(BookAssetModel.sha256 == sha256.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def for_book(self, book_id: BookId) -> BookAsset | None:
        stmt = (
            select(BookAssetModel)
            .join(BookModel, BookModel.primary_asset_id == BookAssetModel.id)
            .where(BookModel.id == book_id.value)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: BookAssetModel) -> BookAsset:
        return BookAsset(
            id=BookAssetId(model.id),
            sha256=Sha256(model.sha256),
            format=BookAssetFormat(model.format),
            mime_type=MimeType(model.mime_type),
            file_size_bytes=FileSizeBytes(model.file_size_bytes),
            storage_backend=StorageBackend(model.storage_backend),
            storage_key=StorageKey(model.storage_key),
            original_filename=OriginalFilename(model.original_filename),
            created_by_user_id=(
                UserId(model.created_by_user_id)
                if model.created_by_user_id is not None
                else None
            ),
            processing_status=ProcessingStatus(model.processing_status),
            processing_error=(
                ProcessingError(model.processing_error)
                if model.processing_error
                else None
            ),
            page_count=(
                PageCount(model.page_count) if model.page_count is not None else None
            ),
            word_count=(
                WordCount(model.word_count) if model.word_count is not None else None
            ),
            total_chunks=(
                TotalChunks(model.total_chunks)
                if model.total_chunks is not None
                else None
            ),
            has_images=model.has_images,
            toc_extracted=model.toc_extracted,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
