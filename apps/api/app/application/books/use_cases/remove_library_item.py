from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

from app.application.books.use_cases.delete_book_asset import DeleteBookAsset
from app.application.books.use_cases.delete_catalog_book import DeleteCatalogBook
from app.application.common.errors import ConflictError, NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.infrastructure.cache.keys import book_ownership_key

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.book_asset.value_objects import BookAssetId
    from app.infrastructure.cache.redis_cache import RedisCache
    from app.infrastructure.storage.file_storage import FileStorage


class RemoveLibraryItem:
    """Remove a user's library grant for a book.

    Three-tier cascade:
      1. Delete the user's active `LibraryItem` for the book (always).
      2. If no other active library items and no listings reference the
         book, delete the catalog `Book` row.
      3. If step 2 ran and no other catalog book references the asset,
         delete the `BookAsset` row and the storage blob.

    Steps 2 and 3 are skipped when reference rules forbid the teardown —
    deleting *my* library item never implies deleting *your* grant or
    the underlying blob.
    """

    def __init__(
        self,
        uow: AbstractUnitOfWork,
        cache: RedisCache | None = None,
        file_storage: FileStorage | None = None,
    ) -> None:
        self._uow = uow
        self._cache = cache
        self._file_storage = file_storage

    async def execute(self, *, book_id: UUID, owner_user_id: UUID) -> None:
        typed_book_id = BookId(book_id)
        typed_user_id = UserId(owner_user_id)

        item = await self._uow.library_items.get_active_for_user_book(
            user_id=typed_user_id,
            book_id=typed_book_id,
        )
        if item is None:
            raise NotFoundError("Book not found")

        await self._uow.library_items.delete(item_id=item.id)
        await self._uow.commit()

        if self._cache is not None:
            await self._cache.delete(
                book_ownership_key(str(owner_user_id), str(book_id))
            )

        asset_id = await self._maybe_delete_catalog_book(typed_book_id)
        if asset_id is not None and self._file_storage is not None:
            await self._maybe_delete_asset(asset_id)

    async def _maybe_delete_catalog_book(
        self, book_id: BookId
    ) -> BookAssetId | None:
        try:
            return await DeleteCatalogBook(self._uow).execute(book_id=book_id)
        except ConflictError:
            return None

    async def _maybe_delete_asset(self, asset_id: BookAssetId) -> None:
        assert self._file_storage is not None
        with suppress(ConflictError):
            await DeleteBookAsset(self._uow, self._file_storage).execute(
                asset_id=asset_id,
            )
