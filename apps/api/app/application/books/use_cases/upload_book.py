from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.application.book_assets.use_cases import (
    AssetRegistration,
    RegisterAssetForProcessing,
)
from app.domain.auth.value_objects import UserId
from app.domain.book_asset.value_objects import BookAssetId
from app.domain.books.entities import Book
from app.domain.books.value_objects import (
    BookDocumentType,
    BookSourceFilename,
    BookTitle,
)
from app.domain.library_item.entities import LibraryItem
from app.domain.library_item.value_objects import LibrarySourceKind

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.book_asset.entities import BookAsset
    from app.infrastructure.storage.file_storage import FileStorage


@dataclass(frozen=True, slots=True)
class UploadBookResult:
    book: Book
    asset: BookAsset
    library_item: LibraryItem


class UploadBook:
    def __init__(self, uow: AbstractUnitOfWork, file_storage: FileStorage) -> None:
        self._uow = uow
        self._file_storage = file_storage

    async def execute(
        self,
        *,
        owner_user_id: UUID,
        title: str,
        source_filename: str,
        file_content: bytes,
        document_type: str = BookDocumentType.BOOK.value,
    ) -> UploadBookResult:
        user_id = UserId(owner_user_id)

        prospective_asset_id = BookAssetId.generate()
        prospective_storage_key = (
            f"assets/{prospective_asset_id.value}/{source_filename}"
        )
        await self._file_storage.store(
            storage_key=prospective_storage_key,
            content=file_content,
        )

        registration = AssetRegistration(
            sha256=hashlib.sha256(file_content).hexdigest(),
            storage_key=prospective_storage_key,
            file_size_bytes=len(file_content),
            original_filename=source_filename,
            created_by_user_id=owner_user_id,
            asset_id=prospective_asset_id.value,
        )
        result = await RegisterAssetForProcessing(self._uow).execute(registration)

        if not result.created:
            await self._file_storage.delete(storage_key=prospective_storage_key)

        asset = result.asset

        book = Book.create(
            primary_asset_id=asset.id,
            title=BookTitle(title),
            created_by_user_id=user_id,
            source_filename=(
                BookSourceFilename(source_filename) if source_filename else None
            ),
            document_type=BookDocumentType(document_type),
        )

        library_item = LibraryItem.create(
            user_id=user_id,
            book_id=book.id,
            source_kind=LibrarySourceKind.UPLOAD,
        )

        await self._uow.books.save(book)
        await self._uow.library_items.save(library_item)
        await self._uow.commit()

        if result.needs_processing:
            RegisterAssetForProcessing.enqueue_processing(asset.id)

        return UploadBookResult(book=book, asset=asset, library_item=library_item)
