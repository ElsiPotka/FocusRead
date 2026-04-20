from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.books.use_cases.remove_library_item import RemoveLibraryItem
from app.application.common.errors import NotFoundError
from app.application.common.unit_of_work import AbstractUnitOfWork
from app.domain.auth.value_objects import UserId
from app.domain.book_asset.entities import BookAsset
from app.domain.book_asset.repositories import BookAssetRepository
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
from app.domain.books.entities import Book
from app.domain.books.repositories import BookRepository
from app.domain.books.value_objects import BookId, BookTitle
from app.domain.library_item.entities import LibraryItem
from app.domain.library_item.repositories import LibraryItemRepository
from app.domain.library_item.value_objects import (
    LibrarySourceKind,
)
from app.domain.marketplace_listing.repositories import MarketplaceListingRepository
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.storage.file_storage import FileStorage


@pytest.fixture
def book_repo():
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def book_asset_repo():
    return AsyncMock(spec=BookAssetRepository)


@pytest.fixture
def library_item_repo():
    return AsyncMock(spec=LibraryItemRepository)


@pytest.fixture
def marketplace_listing_repo():
    return AsyncMock(spec=MarketplaceListingRepository)


@pytest.fixture
def uow(book_repo, book_asset_repo, library_item_repo, marketplace_listing_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.books = book_repo
    mock.book_assets = book_asset_repo
    mock.library_items = library_item_repo
    mock.marketplace_listings = marketplace_listing_repo
    return mock


@pytest.fixture
def cache():
    return AsyncMock(spec=RedisCache)


@pytest.fixture
def file_storage():
    return AsyncMock(spec=FileStorage)


def _make_library_item(*, user_id, book_id) -> LibraryItem:
    return LibraryItem.create(
        user_id=UserId(user_id),
        book_id=BookId(book_id),
        source_kind=LibrarySourceKind.UPLOAD,
    )


def _make_book(*, owner_id, asset_id) -> Book:
    return Book.create(
        primary_asset_id=BookAssetId(asset_id),
        title=BookTitle("Focused Reading"),
        created_by_user_id=UserId(owner_id),
    )


def _make_asset(*, asset_id, owner_id) -> BookAsset:
    now = datetime.now(UTC)
    return BookAsset(
        id=BookAssetId(asset_id),
        sha256=Sha256("a" * 64),
        format=BookAssetFormat.PDF,
        mime_type=MimeType("application/pdf"),
        file_size_bytes=FileSizeBytes(42),
        storage_backend=StorageBackend.LOCAL,
        storage_key=StorageKey(f"assets/{asset_id}/x.pdf"),
        original_filename=OriginalFilename("x.pdf"),
        created_by_user_id=UserId(owner_id),
        processing_status=ProcessingStatus.READY,
        created_at=now,
        updated_at=now,
    )


async def test_removes_library_item_and_cascades_to_book_and_asset(
    uow,
    book_repo,
    book_asset_repo,
    library_item_repo,
    marketplace_listing_repo,
    cache,
    file_storage,
):
    owner_id = uuid4()
    asset_id = uuid4()
    book = _make_book(owner_id=owner_id, asset_id=asset_id)
    item = _make_library_item(user_id=owner_id, book_id=book.id.value)

    library_item_repo.get_active_for_user_book.return_value = item
    library_item_repo.count_active_for_book.return_value = 0
    marketplace_listing_repo.count_active_for_book.return_value = 0
    book_repo.get.return_value = book
    book_repo.count_referencing_asset.return_value = 0
    book_asset_repo.get.return_value = _make_asset(
        asset_id=asset_id, owner_id=owner_id
    )

    await RemoveLibraryItem(uow, cache, file_storage).execute(
        book_id=book.id.value,
        owner_user_id=owner_id,
    )

    library_item_repo.delete.assert_awaited_once_with(item_id=item.id)
    book_repo.delete.assert_awaited_once_with(book_id=book.id)
    book_asset_repo.delete.assert_awaited_once_with(asset_id=book.primary_asset_id)
    file_storage.delete.assert_awaited_once()
    delete_kwargs = file_storage.delete.call_args.kwargs
    assert delete_kwargs["storage_key"].endswith("x.pdf")


async def test_keeps_book_and_asset_when_other_library_items_exist(
    uow,
    book_repo,
    book_asset_repo,
    library_item_repo,
    marketplace_listing_repo,
    cache,
    file_storage,
):
    owner_id = uuid4()
    other_owner_id = uuid4()
    asset_id = uuid4()
    book = _make_book(owner_id=owner_id, asset_id=asset_id)
    item = _make_library_item(user_id=owner_id, book_id=book.id.value)

    library_item_repo.get_active_for_user_book.return_value = item
    library_item_repo.count_active_for_book.return_value = 1  # another grant survives
    marketplace_listing_repo.count_active_for_book.return_value = 0

    await RemoveLibraryItem(uow, cache, file_storage).execute(
        book_id=book.id.value,
        owner_user_id=owner_id,
    )

    library_item_repo.delete.assert_awaited_once_with(item_id=item.id)
    book_repo.delete.assert_not_called()
    book_asset_repo.delete.assert_not_called()
    file_storage.delete.assert_not_called()
    _ = other_owner_id  # the other user's grant is preserved (not touched)


async def test_keeps_book_when_marketplace_listing_references_it(
    uow,
    book_repo,
    book_asset_repo,
    library_item_repo,
    marketplace_listing_repo,
    cache,
    file_storage,
):
    owner_id = uuid4()
    asset_id = uuid4()
    book = _make_book(owner_id=owner_id, asset_id=asset_id)
    item = _make_library_item(user_id=owner_id, book_id=book.id.value)

    library_item_repo.get_active_for_user_book.return_value = item
    library_item_repo.count_active_for_book.return_value = 0
    marketplace_listing_repo.count_active_for_book.return_value = 1  # listing alive
    book_repo.get.return_value = book

    await RemoveLibraryItem(uow, cache, file_storage).execute(
        book_id=book.id.value,
        owner_user_id=owner_id,
    )

    library_item_repo.delete.assert_awaited_once_with(item_id=item.id)
    book_repo.delete.assert_not_called()
    book_asset_repo.delete.assert_not_called()
    file_storage.delete.assert_not_called()


async def test_keeps_asset_when_another_book_references_it(
    uow,
    book_repo,
    book_asset_repo,
    library_item_repo,
    marketplace_listing_repo,
    cache,
    file_storage,
):
    owner_id = uuid4()
    asset_id = uuid4()
    book = _make_book(owner_id=owner_id, asset_id=asset_id)
    item = _make_library_item(user_id=owner_id, book_id=book.id.value)

    library_item_repo.get_active_for_user_book.return_value = item
    library_item_repo.count_active_for_book.return_value = 0
    marketplace_listing_repo.count_active_for_book.return_value = 0
    book_repo.get.return_value = book
    book_repo.count_referencing_asset.return_value = 1  # another book shares the asset
    book_asset_repo.get.return_value = _make_asset(
        asset_id=asset_id, owner_id=owner_id
    )

    await RemoveLibraryItem(uow, cache, file_storage).execute(
        book_id=book.id.value,
        owner_user_id=owner_id,
    )

    library_item_repo.delete.assert_awaited_once_with(item_id=item.id)
    book_repo.delete.assert_awaited_once_with(book_id=book.id)
    book_asset_repo.delete.assert_not_called()
    file_storage.delete.assert_not_called()


async def test_raises_when_user_has_no_library_item_for_book(
    uow, library_item_repo, cache, file_storage
):
    library_item_repo.get_active_for_user_book.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await RemoveLibraryItem(uow, cache, file_storage).execute(
            book_id=uuid4(),
            owner_user_id=uuid4(),
        )


async def test_invalidates_book_ownership_cache(
    uow, book_repo, library_item_repo, marketplace_listing_repo, cache, file_storage
):
    owner_id = uuid4()
    asset_id = uuid4()
    book = _make_book(owner_id=owner_id, asset_id=asset_id)
    item = _make_library_item(user_id=owner_id, book_id=book.id.value)

    library_item_repo.get_active_for_user_book.return_value = item
    library_item_repo.count_active_for_book.return_value = 1
    marketplace_listing_repo.count_active_for_book.return_value = 0

    await RemoveLibraryItem(uow, cache, file_storage).execute(
        book_id=book.id.value,
        owner_user_id=owner_id,
    )

    cache.delete.assert_awaited_once()
    cached_key = cache.delete.call_args.args[0]
    assert str(owner_id) in cached_key
    assert str(book.id.value) in cached_key


async def test_library_item_removal_does_not_require_cache_or_storage(
    uow, library_item_repo, marketplace_listing_repo
):
    owner_id = uuid4()
    asset_id = uuid4()
    book = _make_book(owner_id=owner_id, asset_id=asset_id)
    item = _make_library_item(user_id=owner_id, book_id=book.id.value)

    library_item_repo.get_active_for_user_book.return_value = item
    library_item_repo.count_active_for_book.return_value = 1
    marketplace_listing_repo.count_active_for_book.return_value = 0

    await RemoveLibraryItem(uow).execute(
        book_id=book.id.value,
        owner_user_id=owner_id,
    )

    library_item_repo.delete.assert_awaited_once_with(item_id=item.id)
