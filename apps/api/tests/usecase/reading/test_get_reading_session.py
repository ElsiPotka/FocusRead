from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.common.unit_of_work import AbstractUnitOfWork
from app.application.reading.use_cases.get_reading_session import GetReadingSession
from app.domain.auth.value_objects import UserId
from app.domain.books.entities import Book
from app.domain.books.repositories import BookRepository
from app.domain.books.value_objects import BookFilePath, BookTitle
from app.domain.library_item.entities import LibraryItem
from app.domain.library_item.repositories import LibraryItemRepository
from app.domain.library_item.value_objects import LibrarySourceKind
from app.domain.reading_sessions.entities import ReadingSession
from app.domain.reading_sessions.repositories import ReadingSessionRepository
from app.infrastructure.cache.redis_cache import RedisCache


@pytest.fixture
def book_repo():
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def session_repo():
    return AsyncMock(spec=ReadingSessionRepository)


@pytest.fixture
def library_item_repo():
    return AsyncMock(spec=LibraryItemRepository)


@pytest.fixture
def uow(book_repo, session_repo, library_item_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.books = book_repo
    mock.library_items = library_item_repo
    mock.reading_sessions = session_repo
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


@pytest.fixture
def reading_session(library_item: LibraryItem) -> ReadingSession:
    return ReadingSession.create(library_item_id=library_item.id)


async def test_returns_existing_session(
    uow,
    book_repo,
    session_repo,
    cache,
    library_item_repo,
    book,
    library_item,
    reading_session,
):
    book_repo.get_for_owner.return_value = book
    library_item_repo.get_active_for_user_book.return_value = library_item
    cache.get_json.return_value = None
    session_repo.get_for_library_item.return_value = reading_session

    result = await GetReadingSession(uow, cache).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
    )

    assert result == reading_session
    cache.set_json.assert_awaited_once()


async def test_returns_none_when_no_session(
    uow, book_repo, session_repo, cache, library_item_repo, book, library_item
):
    book_repo.get_for_owner.return_value = book
    library_item_repo.get_active_for_user_book.return_value = library_item
    cache.get_json.return_value = None
    session_repo.get_for_library_item.return_value = None

    result = await GetReadingSession(uow, cache).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
    )

    assert result is None
    cache.set_json.assert_not_awaited()


async def test_cache_hit_refreshes_ttl(
    uow,
    book_repo,
    session_repo,
    cache,
    library_item_repo,
    book,
    library_item,
    reading_session,
):
    book_repo.get_for_owner.return_value = book
    library_item_repo.get_active_for_user_book.return_value = library_item
    cache.get_json.return_value = {"current_word_index": 0}
    session_repo.get_for_library_item.return_value = reading_session

    await GetReadingSession(uow, cache).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
    )

    cache.touch.assert_awaited_once()
    cache.set_json.assert_not_awaited()


async def test_book_not_found_raises(uow, book_repo, cache):
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await GetReadingSession(uow, cache).execute(
            book_id=uuid4(),
            user_id=uuid4(),
        )
