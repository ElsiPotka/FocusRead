from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.common.unit_of_work import AbstractUnitOfWork
from app.application.reading.use_cases.upsert_progress import (
    ProgressUpdate,
    UpsertProgress,
)
from app.domain.auth.value_objects import UserId
from app.domain.books.entities import Book
from app.domain.books.repositories import BookRepository
from app.domain.books.value_objects import BookFilePath, BookTitle
from app.domain.library_item.entities import LibraryItem
from app.domain.library_item.repositories import LibraryItemRepository
from app.domain.library_item.value_objects import LibrarySourceKind
from app.domain.reading_sessions.repositories import ReadingSessionRepository
from app.domain.reading_stats.repositories import ReadingStatRepository
from app.infrastructure.cache.redis_cache import RedisCache


@pytest.fixture
def book_repo():
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def session_repo():
    return AsyncMock(spec=ReadingSessionRepository)


@pytest.fixture
def stat_repo():
    return AsyncMock(spec=ReadingStatRepository)


@pytest.fixture
def library_item_repo():
    return AsyncMock(spec=LibraryItemRepository)


@pytest.fixture
def uow(book_repo, session_repo, stat_repo, library_item_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.books = book_repo
    mock.library_items = library_item_repo
    mock.reading_sessions = session_repo
    mock.reading_stats = stat_repo
    return mock


@pytest.fixture
def cache():
    return AsyncMock(spec=RedisCache)


@pytest.fixture
def book() -> Book:
    return Book.create(
        owner_user_id=UserId(uuid4()),
        title=BookTitle("Test"),
        file_path=BookFilePath("/tmp/test.pdf"),
    )


@pytest.fixture
def library_item(book: Book) -> LibraryItem:
    return LibraryItem.create(
        user_id=book.owner_user_id,
        book_id=book.id,
        source_kind=LibrarySourceKind.UPLOAD,
    )


async def test_creates_new_session_when_none_exists(
    uow,
    book_repo,
    session_repo,
    stat_repo,
    cache,
    library_item_repo,
    book,
    library_item,
):
    book_repo.get_for_owner.return_value = book
    library_item_repo.get_active_for_user_book.return_value = library_item
    session_repo.get_for_library_item.return_value = None
    stat_repo.get.return_value = None

    result = await UpsertProgress(uow, cache).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
        update=ProgressUpdate(current_word_index=100, current_chunk=0),
    )

    assert result.current_word_index.value == 100
    session_repo.save.assert_awaited_once()
    uow.commit.assert_awaited_once()


async def test_updates_existing_session(
    uow,
    book_repo,
    session_repo,
    stat_repo,
    cache,
    library_item_repo,
    book,
    library_item,
):
    from app.domain.reading_sessions.entities import ReadingSession

    existing = ReadingSession.create(library_item_id=library_item.id)
    book_repo.get_for_owner.return_value = book
    library_item_repo.get_active_for_user_book.return_value = library_item
    session_repo.get_for_library_item.return_value = existing
    stat_repo.get.return_value = None

    result = await UpsertProgress(uow, cache).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
        update=ProgressUpdate(current_word_index=500, current_chunk=1, wpm_speed=400),
    )

    assert result.current_word_index.value == 500
    assert result.wpm_speed.value == 400


async def test_saves_reading_stat_with_deltas(
    uow,
    book_repo,
    session_repo,
    stat_repo,
    cache,
    library_item_repo,
    book,
    library_item,
):
    book_repo.get_for_owner.return_value = book
    library_item_repo.get_active_for_user_book.return_value = library_item
    session_repo.get_for_library_item.return_value = None
    stat_repo.get.return_value = None

    await UpsertProgress(uow, cache).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
        update=ProgressUpdate(
            current_word_index=200,
            current_chunk=0,
            words_read_delta=200,
            time_spent_delta_sec=30,
        ),
    )

    stat_repo.save.assert_awaited_once()
    saved_stat = stat_repo.save.call_args[0][0]
    assert saved_stat.words_read.value == 200
    assert saved_stat.time_spent_sec.value == 30


async def test_updates_cache_after_save(
    uow,
    book_repo,
    session_repo,
    stat_repo,
    cache,
    library_item_repo,
    book,
    library_item,
):
    book_repo.get_for_owner.return_value = book
    library_item_repo.get_active_for_user_book.return_value = library_item
    session_repo.get_for_library_item.return_value = None
    stat_repo.get.return_value = None

    await UpsertProgress(uow, cache).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
        update=ProgressUpdate(current_word_index=50, current_chunk=0),
    )

    cache.set_json.assert_awaited_once()


async def test_book_not_found_raises(uow, book_repo, cache):
    cache.get_json.return_value = None
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await UpsertProgress(uow, cache).execute(
            book_id=uuid4(),
            user_id=uuid4(),
            update=ProgressUpdate(current_word_index=0, current_chunk=0),
        )
