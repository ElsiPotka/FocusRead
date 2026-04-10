from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.shelves import DeleteShelf


async def test_delete_shelf(uow, user_id, shelf, shelf_repo):
    shelf_repo.get_for_owner.return_value = shelf

    use_case = DeleteShelf(uow)
    await use_case.execute(shelf_id=shelf.id.value, user_id=user_id.value)

    shelf_repo.delete.assert_awaited_once_with(shelf.id)
    uow.commit.assert_awaited_once()


async def test_delete_shelf_not_found(uow, shelf_repo):
    shelf_repo.get_for_owner.return_value = None

    use_case = DeleteShelf(uow)
    with pytest.raises(NotFoundError, match="Shelf not found"):
        await use_case.execute(shelf_id=uuid4(), user_id=uuid4())
