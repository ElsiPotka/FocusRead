from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.security import SecurityScopes  # noqa: TC002
from fastapi.testclient import TestClient

from app.application.common.errors import ApplicationError
from app.domain.auth.value_objects import Email, UserId
from app.domain.books.entities import Book
from app.domain.books.value_objects import (
    BookDescription,
    BookDocumentType,
    BookFilePath,
    BookId,
    BookPageCount,
    BookPublisher,
    BookTitle,
)
from app.domain.user.entities import User
from app.infrastructure.cache.redis import get_cache
from app.infrastructure.config.settings import settings
from app.infrastructure.persistence.unit_of_work import get_uow
from app.infrastructure.storage.file_storage import get_file_storage
from app.presentation.api.exception_handlers import register_exception_handlers
from app.presentation.api.middleware.auth import get_current_user
from app.presentation.api.routers.books import router as books_router


def _build_user() -> User:
    return User(
        id=UserId(uuid4()),
        name="Reader",
        surname="User",
        email=Email("reader@example.com"),
        email_verified=True,
        is_active=True,
    )


def _build_book() -> Book:
    return Book(
        id=BookId(uuid4()),
        owner_user_id=UserId(uuid4()),
        title=BookTitle("Deep Work"),
        subtitle=None,
        document_type=BookDocumentType.BOOK,
        description=BookDescription("Focus better by training attention."),
        language=None,
        source_filename=None,
        file_path=BookFilePath("/tmp/deep-work.pdf"),
        cover_image_path=None,
        publisher=BookPublisher("Cal Newport"),
        published_year=None,
        page_count=BookPageCount(304),
        word_count=None,
        total_chunks=None,
        has_images=False,
        toc_extracted=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _build_uow(**attrs):
    attrs.setdefault("commit", AsyncMock())
    return SimpleNamespace(**attrs)


def _create_client(*, uow, cache=None, storage=None) -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(books_router, prefix=settings.API_V1_PREFIX)

    async def fake_get_current_user(security_scopes: SecurityScopes) -> User:
        for scope in security_scopes.scopes:
            if scope != "me":
                raise ApplicationError("Not enough permissions", status_code=403)
        return _build_user()

    app.dependency_overrides[get_current_user] = fake_get_current_user
    app.dependency_overrides[get_uow] = lambda: uow
    if cache is not None:
        app.dependency_overrides[get_cache] = lambda: cache
    if storage is not None:
        app.dependency_overrides[get_file_storage] = lambda: storage
    return TestClient(app)


class TestBooksRoutes:
    def test_lists_books(self):
        first = _build_book()
        second = _build_book()
        books = SimpleNamespace(
            list_for_owner=AsyncMock(return_value=[first, second]),
            get_for_owner=AsyncMock(),
            save=AsyncMock(),
            delete=AsyncMock(),
        )
        client = _create_client(uow=_build_uow(books=books))

        response = client.get(f"{settings.API_V1_PREFIX}/books")

        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True
        assert payload["count"] == 2
        assert payload["message"] == "Books retrieved"

    def test_gets_book(self):
        book = _build_book()
        books = SimpleNamespace(
            list_for_owner=AsyncMock(),
            get_for_owner=AsyncMock(return_value=book),
            save=AsyncMock(),
            delete=AsyncMock(),
        )
        client = _create_client(uow=_build_uow(books=books))

        response = client.get(f"{settings.API_V1_PREFIX}/books/{book.id.value}")

        assert response.status_code == 200
        assert response.json()["data"]["title"] == "Deep Work"

    def test_updates_book(self):
        book = _build_book()
        books = SimpleNamespace(
            list_for_owner=AsyncMock(),
            get_for_owner=AsyncMock(return_value=book),
            save=AsyncMock(),
            delete=AsyncMock(),
        )
        uow = _build_uow(books=books)
        client = _create_client(uow=uow)

        response = client.patch(
            f"{settings.API_V1_PREFIX}/books/{book.id.value}",
            json={
                "title": "Updated Book",
                "document_type": "paper",
                "publisher": "Acme Press",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["message"] == "Book updated"
        assert payload["data"]["title"] == "Updated Book"
        assert payload["data"]["document_type"] == "paper"
        assert payload["data"]["publisher"] == "Acme Press"
        books.save.assert_awaited_once_with(book)
        uow.commit.assert_awaited_once()

    def test_deletes_book(self):
        book = _build_book()
        item = SimpleNamespace(id=uuid4())
        books = SimpleNamespace(
            list_for_owner=AsyncMock(),
            get_for_owner=AsyncMock(return_value=book),
            get=AsyncMock(return_value=book),
            save=AsyncMock(),
            delete=AsyncMock(),
        )
        library_items = SimpleNamespace(
            get_active_for_user_book=AsyncMock(return_value=item),
            delete=AsyncMock(),
            count_active_for_book=AsyncMock(return_value=1),
        )
        marketplace_listings = SimpleNamespace(
            count_active_for_book=AsyncMock(return_value=0),
        )
        book_assets = SimpleNamespace(
            get=AsyncMock(),
            delete=AsyncMock(),
        )
        cache = AsyncMock()
        storage = AsyncMock()
        uow = _build_uow(
            books=books,
            library_items=library_items,
            marketplace_listings=marketplace_listings,
            book_assets=book_assets,
        )
        client = _create_client(uow=uow, cache=cache, storage=storage)

        response = client.delete(f"{settings.API_V1_PREFIX}/books/{book.id.value}")

        assert response.status_code == 200
        assert response.json() == {"success": True, "message": "Book deleted"}
        library_items.delete.assert_awaited_once_with(item_id=item.id)
        books.delete.assert_not_awaited()
        cache.delete.assert_awaited_once()
        uow.commit.assert_awaited_once()

    def test_returns_not_found_for_missing_book(self):
        books = SimpleNamespace(
            list_for_owner=AsyncMock(),
            get_for_owner=AsyncMock(return_value=None),
            save=AsyncMock(),
            delete=AsyncMock(),
        )
        client = _create_client(uow=_build_uow(books=books))

        response = client.get(f"{settings.API_V1_PREFIX}/books/{uuid4()}")

        assert response.status_code == 404
        assert response.json() == {"success": False, "message": "Book not found"}
