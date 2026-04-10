from __future__ import annotations

from uuid import uuid4

from app.domain.auth.value_objects import UserId
from app.domain.label.entities import Label
from app.domain.label.value_objects import LabelColor, LabelId, LabelName, LabelSlug


def make_label(**kwargs) -> Label:
    defaults: dict = {
        "name": LabelName("Fiction"),
        "slug": LabelSlug("fiction"),
        "owner_user_id": UserId(uuid4()),
    }
    defaults.update(kwargs)
    return Label.create(**defaults)


def test_create_defaults():
    label = make_label()
    assert label.name.value == "Fiction"
    assert label.slug.value == "fiction"
    assert label.owner_user_id is not None
    assert label.color is None
    assert label.is_system is False
    assert label.created_at is not None


def test_create_with_color():
    label = make_label(color=LabelColor("#00ff00"))
    assert label.color is not None
    assert label.color.value == "#00ff00"


def test_create_system_label():
    label = make_label(owner_user_id=None, is_system=True)
    assert label.owner_user_id is None
    assert label.is_system is True


def test_rename():
    label = make_label()
    old_updated = label.updated_at
    label.rename(name=LabelName("Non-Fiction"), slug=LabelSlug("non-fiction"))
    assert label.name.value == "Non-Fiction"
    assert label.slug.value == "non-fiction"
    assert label.updated_at >= old_updated


def test_recolor():
    label = make_label()
    label.recolor(LabelColor("blue"))
    assert label.color is not None
    assert label.color.value == "blue"


def test_recolor_clear():
    label = make_label(color=LabelColor("red"))
    label.recolor(None)
    assert label.color is None


def test_equality_by_id():
    label1 = make_label()
    label2 = Label(
        id=label1.id,
        name=LabelName("Different"),
        slug=LabelSlug("different"),
    )
    assert label1 == label2


def test_inequality_different_ids():
    assert make_label() != make_label()


def test_hash_by_id():
    label = make_label()
    assert hash(label) == hash(LabelId(label.id.value))
