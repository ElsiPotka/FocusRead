from __future__ import annotations

from app.application.shelves import ReorderShelves
from app.domain.shelf.entities import Shelf
from app.domain.shelf.value_objects import ShelfName


async def test_reorder_shelves(uow, user_id, shelf, shelf_repo):
    shelf2 = Shelf.create(user_id=user_id, name=ShelfName("Second"))
    shelf_repo.list_for_user.return_value = [shelf2, shelf]

    use_case = ReorderShelves(uow)
    ordering = [
        {"shelf_id": shelf2.id.value, "sort_order": 0},
        {"shelf_id": shelf.id.value, "sort_order": 1},
    ]

    result = await use_case.execute(
        user_id=user_id.value,
        ordering=ordering,
    )

    shelf_repo.reorder_shelves.assert_awaited_once()
    uow.commit.assert_awaited_once()
    assert len(result) == 2
