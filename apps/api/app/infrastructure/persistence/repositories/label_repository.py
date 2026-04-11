from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import delete, or_, select

from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId  # noqa: TC001
from app.domain.label.entities import Label
from app.domain.label.repositories import LabelRepository
from app.domain.label.value_objects import LabelColor, LabelId, LabelName, LabelSlug
from app.infrastructure.persistence.models.label import BookLabelModel, LabelModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyLabelRepository(LabelRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, label: Label) -> None:
        model = await self.session.get(LabelModel, label.id.value)

        if model is None:
            model = LabelModel(
                id=label.id.value,
                owner_user_id=label.owner_user_id.value if label.owner_user_id else None,
                name=label.name.value,
                slug=label.slug.value,
                color=label.color.value if label.color else None,
                is_system=label.is_system,
                created_at=label.created_at,
                updated_at=label.updated_at,
            )
            self.session.add(model)
            return

        model.name = label.name.value
        model.slug = label.slug.value
        model.color = label.color.value if label.color else None
        model.updated_at = label.updated_at

    async def get(self, label_id: LabelId) -> Label | None:
        model = await self.session.get(LabelModel, label_id.value)
        if model is None:
            return None
        return self._to_entity(model)

    async def get_for_owner(
        self, *, label_id: LabelId, user_id: UserId
    ) -> Label | None:
        stmt = select(LabelModel).where(
            LabelModel.id == label_id.value,
            LabelModel.owner_user_id == user_id.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def get_by_slug(
        self, *, slug: LabelSlug, user_id: UserId
    ) -> Label | None:
        stmt = select(LabelModel).where(
            LabelModel.slug == slug.value,
            LabelModel.owner_user_id == user_id.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def list_for_user(self, *, user_id: UserId) -> list[Label]:
        stmt = (
            select(LabelModel)
            .where(
                or_(
                    LabelModel.owner_user_id == user_id.value,
                    LabelModel.is_system.is_(True),
                ),
            )
            .order_by(LabelModel.is_system.desc(), LabelModel.name)
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_system(self, *, label_id: LabelId) -> Label | None:
        stmt = select(LabelModel).where(
            LabelModel.id == label_id.value,
            LabelModel.is_system.is_(True),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def list_system(self) -> list[Label]:
        stmt = (
            select(LabelModel)
            .where(LabelModel.is_system.is_(True))
            .order_by(LabelModel.name)
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def delete(self, label_id: LabelId) -> None:
        stmt = delete(LabelModel).where(LabelModel.id == label_id.value)
        await self.session.execute(stmt)

    async def assign_to_book(
        self, *, label_id: LabelId, book_id: BookId
    ) -> None:
        model = BookLabelModel(
            label_id=label_id.value,
            book_id=book_id.value,
        )
        self.session.add(model)

    async def unassign_from_book(
        self, *, label_id: LabelId, book_id: BookId
    ) -> None:
        stmt = delete(BookLabelModel).where(
            BookLabelModel.label_id == label_id.value,
            BookLabelModel.book_id == book_id.value,
        )
        await self.session.execute(stmt)

    async def list_for_book(self, *, book_id: BookId) -> list[Label]:
        stmt = (
            select(LabelModel)
            .join(BookLabelModel, LabelModel.id == BookLabelModel.label_id)
            .where(BookLabelModel.book_id == book_id.value)
            .order_by(LabelModel.name)
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    @staticmethod
    def _to_entity(model: LabelModel) -> Label:
        return Label(
            id=LabelId(model.id),
            name=LabelName(model.name),
            slug=LabelSlug(model.slug),  # type: ignore[arg-type]  # slug is NOT NULL via __slug_nullable__=False
            owner_user_id=UserId(model.owner_user_id) if model.owner_user_id else None,
            color=LabelColor(model.color) if model.color else None,
            is_system=model.is_system,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
