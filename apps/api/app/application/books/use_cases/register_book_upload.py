from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.application.book_assets.use_cases import (
    AssetRegistration,
    RegisterAssetForProcessing,
)
from app.domain.auth.value_objects import UserId
from app.domain.book_asset.value_objects import StorageBackend
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


@dataclass(frozen=True, slots=True)
class RegisterBookUploadResult:
    book: Book
    asset: BookAsset
    library_item: LibraryItem


class RegisterBookUpload:
    """Register a book from an already-stored asset file.

    Caller has already placed the file in storage and provides asset
    primitives (sha256, size, storage_key). Delegates to the canonical
    `RegisterAssetForProcessing` service so the asset lifecycle and
    worker enqueue path stay aligned with `UploadBook` and future
    merchant ingestion.
    """

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self,
        *,
        owner_user_id: UUID,
        title: str,
        storage_key: str,
        sha256: str,
        file_size_bytes: int,
        original_filename: str,
        mime_type: str = "application/pdf",
        storage_backend: str = StorageBackend.LOCAL.value,
        document_type: str = BookDocumentType.BOOK.value,
    ) -> RegisterBookUploadResult:
        user_id = UserId(owner_user_id)

        registration = AssetRegistration(
            sha256=sha256,
            storage_key=storage_key,
            file_size_bytes=file_size_bytes,
            original_filename=original_filename,
            mime_type=mime_type,
            storage_backend=storage_backend,
            created_by_user_id=owner_user_id,
        )
        result = await RegisterAssetForProcessing(self.uow).execute(registration)
        asset = result.asset

        book = Book.create(
            primary_asset_id=asset.id,
            title=BookTitle(title),
            created_by_user_id=user_id,
            source_filename=BookSourceFilename(original_filename),
            document_type=BookDocumentType(document_type),
        )

        library_item = LibraryItem.create(
            user_id=user_id,
            book_id=book.id,
            source_kind=LibrarySourceKind.UPLOAD,
        )

        await self.uow.books.save(book)
        await self.uow.library_items.save(library_item)
        await self.uow.commit()

        if result.needs_processing:
            RegisterAssetForProcessing.enqueue_processing(asset.id)

        return RegisterBookUploadResult(
            book=book, asset=asset, library_item=library_item
        )
