from __future__ import annotations

from uuid import uuid4

import pytest

from app.domain.auth.value_objects import UserId
from app.domain.shelf.entities import Shelf
from app.domain.shelf.value_objects import (
    ShelfColor,
    ShelfDescription,
    ShelfIcon,
    ShelfId,
    ShelfName,
)


def make_shelf(**kwargs) -> Shelf:
    defaults: dict = {
        "user_id": UserId(uuid4()),
        "name": ShelfName("My Shelf"),
    }
    defaults.update(kwargs)
    return Shelf.create(**defaults)


def test_create_defaults():
    shelf = make_shelf()
    assert shelf.name.value == "My Shelf"
    assert shelf.description is None
    assert shelf.color is None
    assert shelf.icon is None
    assert shelf.is_pinned is False
    assert shelf.sort_order == 0
    assert shelf.created_at is not None
    assert shelf.updated_at is not None


def test_create_with_optional_fields():
    shelf = make_shelf(
        description=ShelfDescription("A great shelf"),
        color=ShelfColor("#ff0000"),
        icon=ShelfIcon("book"),
    )
    assert shelf.description is not None
    assert shelf.description.value == "A great shelf"
    assert shelf.color is not None
    assert shelf.color.value == "#ff0000"
    assert shelf.icon is not None
    assert shelf.icon.value == "book"


def test_rename():
    shelf = make_shelf()
    old_updated = shelf.updated_at
    shelf.rename(
        name=ShelfName("Renamed"),
        description=ShelfDescription("New desc"),
    )
    assert shelf.name.value == "Renamed"
    assert shelf.description is not None
    assert shelf.description.value == "New desc"
    assert shelf.updated_at >= old_updated


def test_rename_clears_description():
    shelf = make_shelf(description=ShelfDescription("Old desc"))
    shelf.rename(name=ShelfName("Same"))
    assert shelf.description is None


def test_restyle():
    shelf = make_shelf()
    shelf.restyle(color=ShelfColor("blue"), icon=ShelfIcon("star"))
    assert shelf.color is not None
    assert shelf.color.value == "blue"
    assert shelf.icon is not None
    assert shelf.icon.value == "star"


def test_restyle_clears():
    shelf = make_shelf(color=ShelfColor("red"))
    shelf.restyle()
    assert shelf.color is None
    assert shelf.icon is None


def test_pin_unpin():
    shelf = make_shelf()
    assert shelf.is_pinned is False
    shelf.pin()
    assert shelf.is_pinned is True
    shelf.unpin()
    assert shelf.is_pinned is False


def test_reorder():
    shelf = make_shelf()
    shelf.reorder(5)
    assert shelf.sort_order == 5


def test_reorder_negative_raises():
    shelf = make_shelf()
    with pytest.raises(ValueError, match="negative"):
        shelf.reorder(-1)


def test_init_negative_sort_order_raises():
    with pytest.raises(ValueError, match="negative"):
        Shelf(
            id=ShelfId.generate(),
            user_id=UserId(uuid4()),
            name=ShelfName("Bad"),
            sort_order=-1,
        )


def test_equality_by_id():
    shelf1 = make_shelf()
    shelf2 = Shelf(
        id=shelf1.id,
        user_id=shelf1.user_id,
        name=ShelfName("Different"),
    )
    assert shelf1 == shelf2


def test_inequality_different_ids():
    assert make_shelf() != make_shelf()
