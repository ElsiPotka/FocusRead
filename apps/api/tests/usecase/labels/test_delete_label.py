from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.labels import DeleteLabel


async def test_delete_label(uow, user_id, label, label_repo):
    label_repo.get_for_owner.return_value = label

    use_case = DeleteLabel(uow)
    await use_case.execute(label_id=label.id.value, user_id=user_id.value)

    label_repo.delete.assert_awaited_once_with(label.id)
    uow.commit.assert_awaited_once()


async def test_delete_label_not_found(uow, label_repo):
    label_repo.get_for_owner.return_value = None

    use_case = DeleteLabel(uow)
    with pytest.raises(NotFoundError, match="Label not found"):
        await use_case.execute(label_id=uuid4(), user_id=uuid4())
