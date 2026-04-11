from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.bookmarks.use_cases.create_bookmark import CreateBookmark
from app.application.common.errors import NotFoundError


async def test_create_bookmark_minimal(uow, book_repo, bookmark_repo, book):
    book_repo.get_for_owner.return_value = book

    result = await CreateBookmark(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
        word_index=100,
    )

    assert result.word_index == 100
    assert result.label is None
    bookmark_repo.save.assert_awaited_once()
    uow.commit.assert_awaited_once()


async def test_create_bookmark_with_label_and_note(uow, book_repo, bookmark_repo, book):
    book_repo.get_for_owner.return_value = book

    result = await CreateBookmark(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
        word_index=500,
        chunk_index=2,
        page_number=15,
        label="Important",
        note="Remember this",
    )

    assert result.word_index == 500
    assert result.label.value == "Important"
    assert result.note.value == "Remember this"


async def test_create_bookmark_book_not_found(uow, book_repo):
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await CreateBookmark(uow).execute(
            book_id=uuid4(),
            user_id=uuid4(),
            word_index=0,
        )
