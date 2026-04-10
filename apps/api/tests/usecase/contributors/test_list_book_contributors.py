from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.contributors import ListBookContributors
from app.domain.contributor.entities import Contributor
from app.domain.contributor.value_objects import (
    ContributorDisplayName,
    ContributorRole,
)


async def test_list_returns_ordered(uow, book, book_repo, contributor_repo):
    book_repo.get_for_owner.return_value = book
    c1 = Contributor.create(display_name=ContributorDisplayName("Author A"))
    c2 = Contributor.create(display_name=ContributorDisplayName("Editor B"))
    contributor_repo.list_for_book.return_value = [
        (c1, ContributorRole.AUTHOR, 0),
        (c2, ContributorRole.EDITOR, 1),
    ]

    use_case = ListBookContributors(uow)
    result = await use_case.execute(
        book_id=book.id.value,
        owner_user_id=book.owner_user_id.value,
    )

    assert len(result) == 2
    assert result[0][0].display_name.value == "Author A"
    assert result[0][1] == ContributorRole.AUTHOR
    assert result[1][2] == 1


async def test_list_empty(uow, book, book_repo, contributor_repo):
    book_repo.get_for_owner.return_value = book
    contributor_repo.list_for_book.return_value = []

    use_case = ListBookContributors(uow)
    result = await use_case.execute(
        book_id=book.id.value,
        owner_user_id=book.owner_user_id.value,
    )

    assert result == []


async def test_list_book_not_found(uow, book_repo):
    book_repo.get_for_owner.return_value = None

    use_case = ListBookContributors(uow)
    with pytest.raises(NotFoundError, match="Book not found"):
        await use_case.execute(
            book_id=uuid4(),
            owner_user_id=uuid4(),
        )
