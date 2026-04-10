from __future__ import annotations

import pytest

from app.application.common.errors import NotFoundError
from app.application.contributors import AttachContributor
from app.domain.contributor.entities import Contributor
from app.domain.contributor.value_objects import (
    ContributorDisplayName,
    ContributorRole,
)


async def test_attach_new_contributor(uow, book, contributor_repo, book_repo):
    book_repo.get_for_owner.return_value = book
    contributor_repo.get_by_display_name.return_value = None
    contributor_repo.list_for_book.side_effect = [
        [],  # before attach
        [
            (
                Contributor.create(display_name=ContributorDisplayName("Author A")),
                ContributorRole.AUTHOR,
                0,
            )
        ],  # after attach
    ]

    use_case = AttachContributor(uow)
    result = await use_case.execute(
        book_id=book.id.value,
        owner_user_id=book.owner_user_id.value,
        contributor_display_name="Author A",
        role="author",
    )

    assert len(result) == 1
    contributor_repo.save.assert_awaited_once()
    contributor_repo.attach_to_book.assert_awaited_once()
    uow.commit.assert_awaited_once()


async def test_attach_existing_contributor(uow, book, contributor_repo, book_repo):
    existing = Contributor.create(display_name=ContributorDisplayName("Author A"))
    book_repo.get_for_owner.return_value = book
    contributor_repo.get_by_display_name.return_value = existing
    contributor_repo.list_for_book.side_effect = [
        [],  # before attach
        [(existing, ContributorRole.AUTHOR, 0)],  # after attach
    ]

    use_case = AttachContributor(uow)
    result = await use_case.execute(
        book_id=book.id.value,
        owner_user_id=book.owner_user_id.value,
        contributor_display_name="Author A",
        role="author",
    )

    assert len(result) == 1
    contributor_repo.save.assert_not_awaited()
    contributor_repo.attach_to_book.assert_awaited_once()


async def test_attach_book_not_found(uow, book_repo):
    book_repo.get_for_owner.return_value = None

    use_case = AttachContributor(uow)
    with pytest.raises(NotFoundError, match="Book not found"):
        await use_case.execute(
            book_id=book_repo.return_value,
            owner_user_id=book_repo.return_value,
            contributor_display_name="Author A",
            role="author",
        )


async def test_attach_auto_increments_position(uow, book, contributor_repo, book_repo):
    existing = Contributor.create(display_name=ContributorDisplayName("Author A"))
    book_repo.get_for_owner.return_value = book
    contributor_repo.get_by_display_name.return_value = None
    contributor_repo.list_for_book.side_effect = [
        [(existing, ContributorRole.AUTHOR, 0)],  # one already exists
        [],  # after (doesn't matter for assertion)
    ]

    use_case = AttachContributor(uow)
    await use_case.execute(
        book_id=book.id.value,
        owner_user_id=book.owner_user_id.value,
        contributor_display_name="Author B",
        role="author",
    )

    call_kwargs = contributor_repo.attach_to_book.call_args.kwargs
    assert call_kwargs["position"] == 1
