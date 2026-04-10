from __future__ import annotations

from app.domain.contributor.entities import Contributor
from app.domain.contributor.value_objects import (
    ContributorDisplayName,
    ContributorId,
    ContributorSortName,
)


def make_contributor(**kwargs) -> Contributor:
    defaults: dict = {
        "display_name": ContributorDisplayName("Jane Doe"),
    }
    defaults.update(kwargs)
    return Contributor.create(**defaults)


def test_create_defaults():
    c = make_contributor()
    assert c.display_name.value == "Jane Doe"
    assert c.sort_name is None
    assert c.created_at is not None
    assert c.updated_at is not None


def test_create_with_sort_name():
    c = make_contributor(sort_name=ContributorSortName("Doe, Jane"))
    assert c.sort_name is not None
    assert c.sort_name.value == "Doe, Jane"


def test_rename_updates_fields():
    c = make_contributor()
    old_updated = c.updated_at
    c.rename(
        display_name=ContributorDisplayName("John Smith"),
        sort_name=ContributorSortName("Smith, John"),
    )
    assert c.display_name.value == "John Smith"
    assert c.sort_name is not None
    assert c.sort_name.value == "Smith, John"
    assert c.updated_at >= old_updated


def test_rename_clears_sort_name():
    c = make_contributor(sort_name=ContributorSortName("Doe, Jane"))
    c.rename(display_name=ContributorDisplayName("Jane Doe"))
    assert c.sort_name is None


def test_equality_by_id():
    c1 = make_contributor()
    c2 = Contributor(
        id=c1.id,
        display_name=ContributorDisplayName("Different Name"),
    )
    assert c1 == c2


def test_inequality_different_ids():
    c1 = make_contributor()
    c2 = make_contributor()
    assert c1 != c2


def test_hash_by_id():
    c = make_contributor()
    assert hash(c) == hash(ContributorId(c.id.value))
