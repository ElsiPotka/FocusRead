from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.domain.shelf.value_objects import (
    ShelfColor,
    ShelfDescription,
    ShelfIcon,
    ShelfId,
    ShelfName,
)

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId


class Shelf:
    def __init__(
        self,
        *,
        id: ShelfId,
        user_id: UserId,
        name: ShelfName,
        description: ShelfDescription | None = None,
        color: ShelfColor | None = None,
        icon: ShelfIcon | None = None,
        is_pinned: bool = False,
        sort_order: int = 0,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        if sort_order < 0:
            raise ValueError("Shelf sort order cannot be negative.")

        self._id = id
        self._user_id = user_id
        self._name = name
        self._description = description
        self._color = color
        self._icon = icon
        self._is_pinned = is_pinned
        self._sort_order = sort_order
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        *,
        user_id: UserId,
        name: ShelfName,
        description: ShelfDescription | None = None,
        color: ShelfColor | None = None,
        icon: ShelfIcon | None = None,
    ) -> Shelf:
        return cls(
            id=ShelfId.generate(),
            user_id=user_id,
            name=name,
            description=description,
            color=color,
            icon=icon,
        )

    @property
    def id(self) -> ShelfId:
        return self._id

    @property
    def user_id(self) -> UserId:
        return self._user_id

    @property
    def name(self) -> ShelfName:
        return self._name

    @property
    def description(self) -> ShelfDescription | None:
        return self._description

    @property
    def color(self) -> ShelfColor | None:
        return self._color

    @property
    def icon(self) -> ShelfIcon | None:
        return self._icon

    @property
    def is_pinned(self) -> bool:
        return self._is_pinned

    @property
    def sort_order(self) -> int:
        return self._sort_order

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def rename(
        self,
        *,
        name: ShelfName,
        description: ShelfDescription | None = None,
    ) -> None:
        self._name = name
        self._description = description
        self._updated_at = datetime.now(UTC)

    def restyle(
        self,
        *,
        color: ShelfColor | None = None,
        icon: ShelfIcon | None = None,
    ) -> None:
        self._color = color
        self._icon = icon
        self._updated_at = datetime.now(UTC)

    def pin(self) -> None:
        self._is_pinned = True
        self._updated_at = datetime.now(UTC)

    def unpin(self) -> None:
        self._is_pinned = False
        self._updated_at = datetime.now(UTC)

    def reorder(self, sort_order: int) -> None:
        if sort_order < 0:
            raise ValueError("Shelf sort order cannot be negative.")
        self._sort_order = sort_order
        self._updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Shelf) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
