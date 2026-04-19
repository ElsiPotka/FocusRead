from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.admin.create_system_label import CreateSystemLabel
from app.application.admin.delete_system_label import DeleteSystemLabel
from app.application.admin.list_system_labels import ListSystemLabels
from app.application.admin.update_system_label import UpdateSystemLabel
from app.application.common.errors import NotFoundError
from app.domain.label.entities import Label
from app.domain.label.value_objects import LabelColor, LabelName, LabelSlug


@pytest.fixture
def system_label() -> Label:
    return Label.create(
        name=LabelName("Fiction"),
        slug=LabelSlug("fiction"),
        owner_user_id=None,
        color=LabelColor("#EC4899"),
        is_system=True,
    )


class TestCreateSystemLabel:
    @pytest.mark.asyncio
    async def test_creates_system_label(self, uow, label_repo):
        use_case = CreateSystemLabel(uow)
        label = await use_case.execute(name="Fiction", color="#EC4899")

        label_repo.save.assert_awaited_once()
        saved = label_repo.save.call_args.args[0]
        assert saved.name.value == "Fiction"
        assert saved.is_system is True
        assert saved.owner_user_id is None
        assert saved.color.value == "#EC4899"
        uow.commit.assert_awaited_once()
        assert label is saved

    @pytest.mark.asyncio
    async def test_creates_without_color(self, uow, label_repo):
        use_case = CreateSystemLabel(uow)
        label = await use_case.execute(name="Reference")

        saved = label_repo.save.call_args.args[0]
        assert saved.color is None
        assert label is saved


class TestListSystemLabels:
    @pytest.mark.asyncio
    async def test_returns_system_labels(self, uow, label_repo, system_label):
        label_repo.list_system.return_value = [system_label]

        use_case = ListSystemLabels(uow)
        result = await use_case.execute()

        label_repo.list_system.assert_awaited_once()
        assert result == [system_label]

    @pytest.mark.asyncio
    async def test_returns_empty(self, uow, label_repo):
        label_repo.list_system.return_value = []

        use_case = ListSystemLabels(uow)
        result = await use_case.execute()

        assert result == []


class TestUpdateSystemLabel:
    @pytest.mark.asyncio
    async def test_renames(self, uow, label_repo, system_label):
        label_repo.get_system.return_value = system_label

        use_case = UpdateSystemLabel(uow)
        result = await use_case.execute(
            label_id=system_label.id.value,
            name="Sci-Fi",
        )

        assert result.name.value == "Sci-Fi"
        label_repo.save.assert_awaited_once()
        uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_recolors(self, uow, label_repo, system_label):
        label_repo.get_system.return_value = system_label

        use_case = UpdateSystemLabel(uow)
        result = await use_case.execute(
            label_id=system_label.id.value,
            color="#FF0000",
        )

        assert result.color is not None
        assert result.color.value == "#FF0000"

    @pytest.mark.asyncio
    async def test_clears_color(self, uow, label_repo, system_label):
        label_repo.get_system.return_value = system_label

        use_case = UpdateSystemLabel(uow)
        result = await use_case.execute(
            label_id=system_label.id.value,
            clear_color=True,
        )

        assert result.color is None

    @pytest.mark.asyncio
    async def test_not_found(self, uow, label_repo):
        label_repo.get_system.return_value = None

        use_case = UpdateSystemLabel(uow)
        with pytest.raises(NotFoundError):
            await use_case.execute(label_id=uuid4(), name="Nope")


class TestDeleteSystemLabel:
    @pytest.mark.asyncio
    async def test_deletes(self, uow, label_repo, system_label):
        label_repo.get_system.return_value = system_label

        use_case = DeleteSystemLabel(uow)
        await use_case.execute(label_id=system_label.id.value)

        label_repo.delete.assert_awaited_once_with(system_label.id)
        uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_not_found(self, uow, label_repo):
        label_repo.get_system.return_value = None

        use_case = DeleteSystemLabel(uow)
        with pytest.raises(NotFoundError):
            await use_case.execute(label_id=uuid4())
