from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import delete, select, update

from app.domain.books.value_objects import BookId  # noqa: TC001
from app.domain.contributor.entities import Contributor
from app.domain.contributor.repositories import ContributorRepository
from app.domain.contributor.value_objects import (
    ContributorDisplayName,
    ContributorId,
    ContributorRole,
    ContributorSortName,
)
from app.infrastructure.persistence.models.contributor import (
    BookContributorModel,
    ContributorModel,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyContributorRepository(ContributorRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, contributor: Contributor) -> None:
        model = await self.session.get(ContributorModel, contributor.id.value)

        if model is None:
            model = ContributorModel(
                id=contributor.id.value,
                display_name=contributor.display_name.value,
                sort_name=contributor.sort_name.value if contributor.sort_name else None,
                created_at=contributor.created_at,
                updated_at=contributor.updated_at,
            )
            self.session.add(model)
            return

        model.display_name = contributor.display_name.value
        model.sort_name = contributor.sort_name.value if contributor.sort_name else None
        model.updated_at = contributor.updated_at

    async def get(self, contributor_id: ContributorId) -> Contributor | None:
        model = await self.session.get(ContributorModel, contributor_id.value)
        if model is None:
            return None
        return self._to_entity(model)

    async def get_by_display_name(
        self, display_name: ContributorDisplayName
    ) -> Contributor | None:
        stmt = select(ContributorModel).where(
            ContributorModel.display_name == display_name.value
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def list_for_book(
        self, *, book_id: BookId
    ) -> list[tuple[Contributor, ContributorRole, int]]:
        stmt = (
            select(ContributorModel, BookContributorModel.role, BookContributorModel.position)
            .join(
                BookContributorModel,
                ContributorModel.id == BookContributorModel.contributor_id,
            )
            .where(BookContributorModel.book_id == book_id.value)
            .order_by(BookContributorModel.position)
        )
        result = await self.session.execute(stmt)
        return [
            (self._to_entity(row[0]), ContributorRole(row[1]), row[2])
            for row in result.all()
        ]

    async def attach_to_book(
        self,
        *,
        book_id: BookId,
        contributor_id: ContributorId,
        role: ContributorRole,
        position: int,
    ) -> None:
        model = BookContributorModel(
            book_id=book_id.value,
            contributor_id=contributor_id.value,
            role=role.value,
            position=position,
        )
        self.session.add(model)

    async def detach_from_book(
        self,
        *,
        book_id: BookId,
        contributor_id: ContributorId,
        role: ContributorRole,
    ) -> None:
        stmt = delete(BookContributorModel).where(
            BookContributorModel.book_id == book_id.value,
            BookContributorModel.contributor_id == contributor_id.value,
            BookContributorModel.role == role.value,
        )
        await self.session.execute(stmt)

    async def reorder_on_book(
        self,
        *,
        book_id: BookId,
        ordering: list[tuple[ContributorId, ContributorRole, int]],
    ) -> None:
        for contributor_id, role, position in ordering:
            stmt = (
                update(BookContributorModel)
                .where(
                    BookContributorModel.book_id == book_id.value,
                    BookContributorModel.contributor_id == contributor_id.value,
                    BookContributorModel.role == role.value,
                )
                .values(position=position)
            )
            await self.session.execute(stmt)

    @staticmethod
    def _to_entity(model: ContributorModel) -> Contributor:
        return Contributor(
            id=ContributorId(model.id),
            display_name=ContributorDisplayName(model.display_name),
            sort_name=ContributorSortName(model.sort_name) if model.sort_name else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
