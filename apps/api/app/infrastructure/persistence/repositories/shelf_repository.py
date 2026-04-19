from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import case, delete, select, update

from app.domain.auth.value_objects import UserId
from app.domain.library_item.value_objects import LibraryItemId
from app.domain.shelf.entities import Shelf
from app.domain.shelf.repositories import ShelfRepository
from app.domain.shelf.value_objects import (
    ShelfColor,
    ShelfDescription,
    ShelfIcon,
    ShelfId,
    ShelfName,
)
from app.infrastructure.persistence.models.shelf import ShelfItemModel, ShelfModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyShelfRepository(ShelfRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, shelf: Shelf) -> None:
        model = await self.session.get(ShelfModel, shelf.id.value)

        if model is None:
            model = ShelfModel(
                id=shelf.id.value,
                user_id=shelf.user_id.value,
                name=shelf.name.value,
                description=shelf.description.value if shelf.description else None,
                color=shelf.color.value if shelf.color else None,
                icon=shelf.icon.value if shelf.icon else None,
                is_pinned=shelf.is_pinned,
                sort_order=shelf.sort_order,
                created_at=shelf.created_at,
                updated_at=shelf.updated_at,
            )
            self.session.add(model)
            return

        model.name = shelf.name.value
        model.description = shelf.description.value if shelf.description else None
        model.color = shelf.color.value if shelf.color else None
        model.icon = shelf.icon.value if shelf.icon else None
        model.is_pinned = shelf.is_pinned
        model.sort_order = shelf.sort_order
        model.updated_at = shelf.updated_at

    async def get(self, shelf_id: ShelfId) -> Shelf | None:
        model = await self.session.get(ShelfModel, shelf_id.value)
        if model is None:
            return None
        return self._to_entity(model)

    async def get_for_owner(
        self, *, shelf_id: ShelfId, user_id: UserId
    ) -> Shelf | None:
        stmt = select(ShelfModel).where(
            ShelfModel.id == shelf_id.value,
            ShelfModel.user_id == user_id.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def list_for_user(self, *, user_id: UserId) -> list[Shelf]:
        stmt = (
            select(ShelfModel)
            .where(ShelfModel.user_id == user_id.value)
            .order_by(ShelfModel.sort_order)
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def delete(self, shelf_id: ShelfId) -> None:
        stmt = delete(ShelfModel).where(ShelfModel.id == shelf_id.value)
        await self.session.execute(stmt)

    async def add_library_item(
        self,
        *,
        shelf_id: ShelfId,
        library_item_id: LibraryItemId,
        sort_order: int,
    ) -> None:
        model = ShelfItemModel(
            shelf_id=shelf_id.value,
            library_item_id=library_item_id.value,
            sort_order=sort_order,
        )
        self.session.add(model)

    async def remove_library_item(
        self, *, shelf_id: ShelfId, library_item_id: LibraryItemId
    ) -> None:
        stmt = delete(ShelfItemModel).where(
            ShelfItemModel.shelf_id == shelf_id.value,
            ShelfItemModel.library_item_id == library_item_id.value,
        )
        await self.session.execute(stmt)

    async def list_library_item_ids(self, *, shelf_id: ShelfId) -> list[LibraryItemId]:
        stmt = (
            select(ShelfItemModel.library_item_id)
            .where(ShelfItemModel.shelf_id == shelf_id.value)
            .order_by(ShelfItemModel.sort_order)
        )
        result = await self.session.execute(stmt)
        return [LibraryItemId(value) for value in result.scalars().all()]

    async def reorder_shelves(self, *, ordering: list[tuple[ShelfId, int]]) -> None:
        if not ordering:
            return
        ids = [shelf_id.value for shelf_id, _ in ordering]
        stmt = (
            update(ShelfModel)
            .where(ShelfModel.id.in_(ids))
            .values(
                sort_order=case(
                    {shelf_id.value: sort_order for shelf_id, sort_order in ordering},
                    value=ShelfModel.id,
                )
            )
        )
        await self.session.execute(stmt)

    async def reorder_items(
        self,
        *,
        shelf_id: ShelfId,
        ordering: list[tuple[LibraryItemId, int]],
    ) -> None:
        if not ordering:
            return

        sort_order_map = {
            library_item_id.value: sort_order
            for library_item_id, sort_order in ordering
        }
        stmt = (
            update(ShelfItemModel)
            .where(
                ShelfItemModel.shelf_id == shelf_id.value,
                ShelfItemModel.library_item_id.in_(list(sort_order_map.keys())),
            )
            .values(
                sort_order=case(
                    sort_order_map,
                    value=ShelfItemModel.library_item_id,
                )
            )
        )
        await self.session.execute(stmt)

    @staticmethod
    def _to_entity(model: ShelfModel) -> Shelf:
        return Shelf(
            id=ShelfId(model.id),
            user_id=UserId(model.user_id),
            name=ShelfName(model.name),
            description=ShelfDescription(model.description)
            if model.description
            else None,
            color=ShelfColor(model.color) if model.color else None,
            icon=ShelfIcon(model.icon) if model.icon else None,
            is_pinned=model.is_pinned,
            sort_order=model.sort_order,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
