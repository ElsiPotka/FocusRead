from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import ConflictError, NotFoundError

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.book_asset.value_objects import BookAssetId
    from app.domain.books.value_objects import BookId


class DeleteCatalogBook:
    """Tear down a catalog `Book` row.

    Reference rules:
      * no active library items may reference the book;
      * no non-archived marketplace listings may reference the book.

    Returns the `primary_asset_id` of the deleted book so callers can
    decide whether to cascade into asset teardown (asset deletion is a
    distinct concern owned by `DeleteBookAsset`).
    """

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, book_id: BookId) -> BookAssetId:
        book = await self._uow.books.get(book_id)
        if book is None:
            raise NotFoundError("Book not found")

        active_library_items = await self._uow.library_items.count_active_for_book(
            book_id=book_id,
        )
        if active_library_items > 0:
            raise ConflictError(
                "Book is still referenced by active library items; "
                "cannot delete from catalog",
            )

        active_listings = await self._uow.marketplace_listings.count_active_for_book(
            book_id=book_id,
        )
        if active_listings > 0:
            raise ConflictError(
                "Book is still referenced by marketplace listings; "
                "cannot delete from catalog",
            )

        asset_id = book.primary_asset_id
        await self._uow.books.delete(book_id=book_id)
        await self._uow.commit()
        return asset_id
