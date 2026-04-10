from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.contributor.entities import Contributor
from app.domain.contributor.value_objects import (
    ContributorDisplayName,
    ContributorRole,
    ContributorSortName,
)

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class AttachContributor:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        book_id: UUID,
        owner_user_id: UUID,
        contributor_display_name: str,
        contributor_sort_name: str | None = None,
        role: str = "author",
    ) -> list[tuple[Contributor, ContributorRole, int]]:
        book = await self._uow.books.get_for_owner(
            book_id=BookId(book_id),
            owner_user_id=UserId(owner_user_id),
        )
        if book is None:
            raise NotFoundError("Book not found")

        display_name = ContributorDisplayName(contributor_display_name)
        contributor = await self._uow.contributors.get_by_display_name(display_name)

        if contributor is None:
            sort_name = (
                ContributorSortName(contributor_sort_name)
                if contributor_sort_name
                else None
            )
            contributor = Contributor.create(
                display_name=display_name,
                sort_name=sort_name,
            )
            await self._uow.contributors.save(contributor)

        current = await self._uow.contributors.list_for_book(book_id=book.id)
        next_position = max((pos for _, _, pos in current), default=-1) + 1

        contributor_role = ContributorRole(role)
        await self._uow.contributors.attach_to_book(
            book_id=book.id,
            contributor_id=contributor.id,
            role=contributor_role,
            position=next_position,
        )

        await self._uow.commit()
        return await self._uow.contributors.list_for_book(book_id=book.id)
