from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.labels import UnassignLabel


async def test_unassign_label(
    uow, user_id, book, label, library_item, book_repo, label_repo, library_item_repo
):
    book_repo.get_for_owner.return_value = book
    library_item_repo.get_active_for_user_book.return_value = library_item

    use_case = UnassignLabel(uow)
    await use_case.execute(
        book_id=book.id.value,
        label_id=label.id.value,
        user_id=user_id.value,
    )

    label_repo.unassign_from_library_item.assert_awaited_once()
    uow.commit.assert_awaited_once()


async def test_unassign_book_not_found(uow, book_repo):
    book_repo.get_for_owner.return_value = None

    use_case = UnassignLabel(uow)
    with pytest.raises(NotFoundError, match="Book not found"):
        await use_case.execute(book_id=uuid4(), label_id=uuid4(), user_id=uuid4())
