from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.books.value_objects import BookId
    from app.domain.contributor.entities import Contributor
    from app.domain.contributor.value_objects import (
        ContributorDisplayName,
        ContributorId,
        ContributorRole,
    )


class ContributorRepository(ABC):
    @abstractmethod
    async def save(self, contributor: Contributor) -> None: ...

    @abstractmethod
    async def get(self, contributor_id: ContributorId) -> Contributor | None: ...

    @abstractmethod
    async def get_by_display_name(
        self, display_name: ContributorDisplayName
    ) -> Contributor | None: ...

    @abstractmethod
    async def list_for_book(
        self, *, book_id: BookId
    ) -> list[tuple[Contributor, ContributorRole, int]]: ...

    @abstractmethod
    async def attach_to_book(
        self,
        *,
        book_id: BookId,
        contributor_id: ContributorId,
        role: ContributorRole,
        position: int,
    ) -> None: ...

    @abstractmethod
    async def detach_from_book(
        self,
        *,
        book_id: BookId,
        contributor_id: ContributorId,
        role: ContributorRole,
    ) -> None: ...

    @abstractmethod
    async def reorder_on_book(
        self,
        *,
        book_id: BookId,
        ordering: list[tuple[ContributorId, ContributorRole, int]],
    ) -> None: ...
