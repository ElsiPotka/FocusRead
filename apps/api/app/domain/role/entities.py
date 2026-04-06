from __future__ import annotations

from datetime import UTC, datetime

from app.domain.role.value_objects import RoleId, RoleName


class Role:
    def __init__(
        self,
        *,
        id: RoleId,
        name: RoleName,
        description: str,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self._id = id
        self._name = name
        self._description = description
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @classmethod
    def create(cls, *, name: RoleName, description: str) -> Role:
        return cls(
            id=RoleId.generate(),
            name=name,
            description=description,
        )

    @property
    def id(self) -> RoleId:
        return self._id

    @property
    def name(self) -> RoleName:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Role) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
