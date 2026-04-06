from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.domain.label.value_objects import LabelColor, LabelId, LabelName, LabelSlug

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId


class Label:
    def __init__(
        self,
        *,
        id: LabelId,
        name: LabelName,
        slug: LabelSlug,
        owner_user_id: UserId | None = None,
        color: LabelColor | None = None,
        is_system: bool = False,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self._id = id
        self._name = name
        self._slug = slug
        self._owner_user_id = owner_user_id
        self._color = color
        self._is_system = is_system
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        *,
        name: LabelName,
        slug: LabelSlug,
        owner_user_id: UserId | None = None,
        color: LabelColor | None = None,
        is_system: bool = False,
    ) -> Label:
        return cls(
            id=LabelId.generate(),
            name=name,
            slug=slug,
            owner_user_id=owner_user_id,
            color=color,
            is_system=is_system,
        )

    @property
    def id(self) -> LabelId:
        return self._id

    @property
    def name(self) -> LabelName:
        return self._name

    @property
    def slug(self) -> LabelSlug:
        return self._slug

    @property
    def owner_user_id(self) -> UserId | None:
        return self._owner_user_id

    @property
    def color(self) -> LabelColor | None:
        return self._color

    @property
    def is_system(self) -> bool:
        return self._is_system

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def rename(self, *, name: LabelName, slug: LabelSlug) -> None:
        self._name = name
        self._slug = slug
        self._updated_at = datetime.now(UTC)

    def recolor(self, color: LabelColor | None) -> None:
        self._color = color
        self._updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Label) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
