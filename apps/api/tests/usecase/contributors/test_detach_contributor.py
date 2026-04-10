from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.contributors import DetachContributor


async def test_detach_contributor(uow, book, book_repo):
    book_repo.get_for_owner.return_value = book

    use_case = DetachContributor(uow)
    await use_case.execute(
        book_id=book.id.value,
        owner_user_id=book.owner_user_id.value,
        contributor_id=uuid4(),
        role="author",
    )

    uow.contributors.detach_from_book.assert_awaited_once()
    uow.commit.assert_awaited_once()


async def test_detach_book_not_found(uow, book_repo):
    book_repo.get_for_owner.return_value = None

    use_case = DetachContributor(uow)
    with pytest.raises(NotFoundError, match="Book not found"):
        await use_case.execute(
            book_id=uuid4(),
            owner_user_id=uuid4(),
            contributor_id=uuid4(),
            role="author",
        )
