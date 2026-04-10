from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.contributor.value_objects import ContributorId, ContributorRole

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class DetachContributor:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        book_id: UUID,
        owner_user_id: UUID,
        contributor_id: UUID,
        role: str = "author",
    ) -> None:
        book = await self._uow.books.get_for_owner(
            book_id=BookId(book_id),
            owner_user_id=UserId(owner_user_id),
        )
        if book is None:
            raise NotFoundError("Book not found")

        await self._uow.contributors.detach_from_book(
            book_id=book.id,
            contributor_id=ContributorId(contributor_id),
            role=ContributorRole(role),
        )
        await self._uow.commit()
