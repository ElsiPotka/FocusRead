from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.books.use_cases.search_books import SearchBooks
from app.domain.auth.value_objects import UserId
from app.domain.books.filter import BookFilter


@pytest.fixture
def user_id():
    return UserId(uuid4())


class TestSearchBooks:
    @pytest.mark.asyncio
    async def test_delegates_to_repo_search(self, uow, book_repo, book, user_id):
        book_repo.search.return_value = [book]
        book_filter = BookFilter(owner_user_id=user_id, query="focused")

        use_case = SearchBooks(uow)
        result = await use_case.execute(book_filter=book_filter)

        book_repo.search.assert_awaited_once_with(book_filter=book_filter)
        assert result == [book]

    @pytest.mark.asyncio
    async def test_returns_empty_list(self, uow, book_repo, user_id):
        book_repo.search.return_value = []
        book_filter = BookFilter(owner_user_id=user_id)

        use_case = SearchBooks(uow)
        result = await use_case.execute(book_filter=book_filter)

        assert result == []
