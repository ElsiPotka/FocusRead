from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.shelves import GetShelf


async def test_get_shelf(uow, user_id, shelf, shelf_repo):
    shelf_repo.get_for_owner.return_value = shelf

    use_case = GetShelf(uow)
    result = await use_case.execute(
        shelf_id=shelf.id.value,
        user_id=user_id.value,
    )

    assert result == shelf


async def test_get_shelf_not_found(uow, shelf_repo):
    shelf_repo.get_for_owner.return_value = None

    use_case = GetShelf(uow)
    with pytest.raises(NotFoundError, match="Shelf not found"):
        await use_case.execute(shelf_id=uuid4(), user_id=uuid4())
