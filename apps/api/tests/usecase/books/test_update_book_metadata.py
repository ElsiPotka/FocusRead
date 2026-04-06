from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.books.use_cases.update_book_metadata import UpdateBookMetadata
from app.application.common.errors import NotFoundError
from app.domain.books.value_objects import BookDocumentType


async def test_update_book_metadata_persists_changes(
    uow,
    book_repo,
    book,
    book_id,
    owner_user_id,
):
    book_repo.get_for_owner.return_value = book

    result = await UpdateBookMetadata(uow).execute(
        book_id=book_id,
        owner_user_id=owner_user_id,
        updates={
            "title": "Updated title",
            "document_type": BookDocumentType.PAPER.value,
            "publisher": "Acme Press",
        },
    )

    assert result.title.value == "Updated title"
    assert result.document_type is BookDocumentType.PAPER
    assert result.publisher is not None
    assert result.publisher.value == "Acme Press"
    book_repo.save.assert_awaited_once_with(book)
    uow.commit.assert_awaited_once()


async def test_update_book_metadata_raises_when_missing(uow, book_repo, owner_user_id):
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await UpdateBookMetadata(uow).execute(
            book_id=uuid4(),
            owner_user_id=owner_user_id,
            updates={"title": "Updated title"},
        )
