from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import ConflictError, NotFoundError

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.book_asset.value_objects import BookAssetId
    from app.infrastructure.storage.file_storage import FileStorage


class DeleteBookAsset:
    """Tear down an asset row and its storage blob.

    Reference rule: the asset must not be referenced by any catalog
    `Book` (via `books.primary_asset_id`). The schema enforces this via
    `ON DELETE RESTRICT`; this use case checks up-front so callers get a
    domain error instead of a driver integrity error.
    """

    def __init__(self, uow: AbstractUnitOfWork, file_storage: FileStorage) -> None:
        self._uow = uow
        self._file_storage = file_storage

    async def execute(self, *, asset_id: BookAssetId) -> None:
        asset = await self._uow.book_assets.get(asset_id)
        if asset is None:
            raise NotFoundError("Asset not found")

        reference_count = await self._uow.books.count_referencing_asset(
            asset_id=asset_id,
        )
        if reference_count > 0:
            raise ConflictError(
                "Asset is still referenced by a catalog book; cannot delete",
            )

        storage_key = asset.storage_key.value
        await self._uow.book_assets.delete(asset_id=asset_id)
        await self._uow.commit()
        await self._file_storage.delete(storage_key=storage_key)
