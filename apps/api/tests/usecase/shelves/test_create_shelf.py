from __future__ import annotations

from app.application.shelves import CreateShelf


async def test_create_shelf(uow, user_id, shelf_repo):
    use_case = CreateShelf(uow)
    result = await use_case.execute(
        user_id=user_id.value,
        name="My Shelf",
        description="A description",
        color="#ff0000",
        icon="book",
    )

    assert result.name.value == "My Shelf"
    assert result.description is not None
    assert result.description.value == "A description"
    shelf_repo.save.assert_awaited_once()
    uow.commit.assert_awaited_once()


async def test_create_shelf_minimal(uow, user_id, shelf_repo):
    use_case = CreateShelf(uow)
    result = await use_case.execute(
        user_id=user_id.value,
        name="Simple",
    )

    assert result.name.value == "Simple"
    assert result.description is None
    assert result.color is None
    assert result.icon is None
