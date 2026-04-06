from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.domain.role.entities import Role
from app.domain.role.repositories import RoleRepository
from app.domain.role.value_objects import RoleId
from app.infrastructure.persistence.models.role import RoleModel, user_roles_table

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.domain.auth.value_objects import UserId
    from app.domain.role.value_objects import RoleName


class SqlAlchemyRoleRepository(RoleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_name(self, name: RoleName) -> Role | None:
        stmt = select(RoleModel).where(RoleModel.name == name)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def get_by_names(self, names: list[RoleName]) -> list[Role]:
        if not names:
            return []

        stmt = (
            select(RoleModel).where(RoleModel.name.in_(names)).order_by(RoleModel.name)
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def list_for_user(self, user_id: UserId) -> list[Role]:
        stmt = (
            select(RoleModel)
            .join(user_roles_table, RoleModel.id == user_roles_table.c.role_id)
            .where(user_roles_table.c.user_id == user_id.value)
            .order_by(RoleModel.name)
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def assign_to_user(self, user_id: UserId, role_id: RoleId) -> None:
        await self.assign_many_to_user(user_id, [role_id])

    async def assign_many_to_user(
        self, user_id: UserId, role_ids: list[RoleId]
    ) -> None:
        if not role_ids:
            return

        stmt = (
            pg_insert(user_roles_table)
            .values(
                [
                    {"user_id": user_id.value, "role_id": role_id.value}
                    for role_id in role_ids
                ]
            )
            .on_conflict_do_nothing(index_elements=["user_id", "role_id"])
        )
        await self.session.execute(stmt)

    async def remove_many_from_user(
        self, user_id: UserId, role_ids: list[RoleId]
    ) -> None:
        if not role_ids:
            return

        stmt = delete(user_roles_table).where(
            user_roles_table.c.user_id == user_id.value,
            user_roles_table.c.role_id.in_([role_id.value for role_id in role_ids]),
        )
        await self.session.execute(stmt)

    @staticmethod
    def _to_entity(model: RoleModel) -> Role:
        return Role(
            id=RoleId(model.id),
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
