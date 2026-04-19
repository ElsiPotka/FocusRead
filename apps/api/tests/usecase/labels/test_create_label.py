from __future__ import annotations

from app.application.labels import CreateLabel
from app.domain.label.entities import Label
from app.domain.label.value_objects import LabelName, LabelSlug


async def test_create_label(uow, user_id, label_repo):
    label_repo.get_by_slug.return_value = None

    use_case = CreateLabel(uow)
    result = await use_case.execute(
        user_id=user_id.value,
        name="Science Fiction",
        color="#0000ff",
    )

    assert result.name.value == "Science Fiction"
    assert result.slug.value == "science-fiction"
    label_repo.save.assert_awaited_once()
    uow.commit.assert_awaited_once()


async def test_create_label_returns_existing_on_duplicate_slug(
    uow, user_id, label_repo
):
    existing = Label.create(
        name=LabelName("Fiction"),
        slug=LabelSlug("fiction"),
        owner_user_id=user_id,
    )
    label_repo.get_by_slug.return_value = existing

    use_case = CreateLabel(uow)
    result = await use_case.execute(
        user_id=user_id.value,
        name="Fiction",
    )

    assert result == existing
    label_repo.save.assert_not_awaited()
    uow.commit.assert_not_awaited()
