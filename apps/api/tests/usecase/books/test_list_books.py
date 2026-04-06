from __future__ import annotations

from app.application.books.use_cases.list_books import ListBooks


async def test_list_books_returns_owner_books(uow, book_repo, book, owner_user_id):
    second_book = book
    book_repo.list_for_owner.return_value = [book, second_book]

    result = await ListBooks(uow).execute(owner_user_id=owner_user_id)

    assert result == [book, second_book]
    book_repo.list_for_owner.assert_awaited_once()
