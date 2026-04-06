from __future__ import annotations

from datetime import UTC, datetime

from app.domain.contributor.value_objects import (
    ContributorDisplayName,
    ContributorId,
    ContributorSortName,
)


class Contributor:
    def __init__(
        self,
        *,
        id: ContributorId,
        display_name: ContributorDisplayName,
        sort_name: ContributorSortName | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self._id = id
        self._display_name = display_name
        self._sort_name = sort_name
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        *,
        display_name: ContributorDisplayName,
        sort_name: ContributorSortName | None = None,
    ) -> Contributor:
        return cls(
            id=ContributorId.generate(),
            display_name=display_name,
            sort_name=sort_name,
        )

    @property
    def id(self) -> ContributorId:
        return self._id

    @property
    def display_name(self) -> ContributorDisplayName:
        return self._display_name

    @property
    def sort_name(self) -> ContributorSortName | None:
        return self._sort_name

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def rename(
        self,
        *,
        display_name: ContributorDisplayName,
        sort_name: ContributorSortName | None = None,
    ) -> None:
        self._display_name = display_name
        self._sort_name = sort_name
        self._updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Contributor) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)
