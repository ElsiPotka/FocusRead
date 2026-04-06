from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId
    from app.domain.role.entities import Role
    from app.domain.role.value_objects import RoleId, RoleName


class RoleRepository(ABC):
    @abstractmethod
    async def get_by_name(self, name: RoleName) -> Role | None: ...

    @abstractmethod
    async def get_by_names(self, names: list[RoleName]) -> list[Role]: ...

    @abstractmethod
    async def list_for_user(self, user_id: UserId) -> list[Role]: ...

    @abstractmethod
    async def assign_to_user(self, user_id: UserId, role_id: RoleId) -> None: ...

    @abstractmethod
    async def assign_many_to_user(
        self, user_id: UserId, role_ids: list[RoleId]
    ) -> None: ...

    @abstractmethod
    async def remove_many_from_user(
        self, user_id: UserId, role_ids: list[RoleId]
    ) -> None: ...
