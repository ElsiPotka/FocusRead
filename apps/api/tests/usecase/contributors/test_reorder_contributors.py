from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.contributors import ReorderContributors
from app.domain.contributor.entities import Contributor
from app.domain.contributor.value_objects import (
    ContributorDisplayName,
    ContributorRole,
)


async def test_reorder_contributors(uow, book, book_repo, contributor_repo):
    book_repo.get_for_owner.return_value = book
    c1 = Contributor.create(display_name=ContributorDisplayName("Author A"))
    c2 = Contributor.create(display_name=ContributorDisplayName("Author B"))
    contributor_repo.list_for_book.return_value = [
        (c2, ContributorRole.AUTHOR, 0),
        (c1, ContributorRole.AUTHOR, 1),
    ]

    use_case = ReorderContributors(uow)
    ordering = [
        {"contributor_id": c2.id.value, "role": "author", "position": 0},
        {"contributor_id": c1.id.value, "role": "author", "position": 1},
    ]

    result = await use_case.execute(
        book_id=book.id.value,
        owner_user_id=book.owner_user_id.value,
        ordering=ordering,
    )

    contributor_repo.reorder_on_book.assert_awaited_once()
    uow.commit.assert_awaited_once()
    assert len(result) == 2


async def test_reorder_book_not_found(uow, book_repo):
    book_repo.get_for_owner.return_value = None

    use_case = ReorderContributors(uow)
    with pytest.raises(NotFoundError, match="Book not found"):
        await use_case.execute(
            book_id=uuid4(),
            owner_user_id=uuid4(),
            ordering=[],
        )
