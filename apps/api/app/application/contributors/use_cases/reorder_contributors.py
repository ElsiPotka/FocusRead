from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.contributor.value_objects import ContributorId, ContributorRole

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.contributor.entities import Contributor


class ContributorOrderingItem(TypedDict):
    contributor_id: UUID
    role: str
    position: int


class ReorderContributors:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        book_id: UUID,
        owner_user_id: UUID,
        ordering: list[ContributorOrderingItem],
    ) -> list[tuple[Contributor, ContributorRole, int]]:
        book = await self._uow.books.get_for_owner(
            book_id=BookId(book_id),
            owner_user_id=UserId(owner_user_id),
        )
        if book is None:
            raise NotFoundError("Book not found")

        parsed = [
            (
                ContributorId(item["contributor_id"]),
                ContributorRole(item["role"]),
                item["position"],
            )
            for item in ordering
        ]

        await self._uow.contributors.reorder_on_book(
            book_id=book.id,
            ordering=parsed,
        )
        await self._uow.commit()
        return await self._uow.contributors.list_for_book(book_id=book.id)
