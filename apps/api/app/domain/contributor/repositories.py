from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.contributor.entities import Contributor
    from app.domain.contributor.value_objects import ContributorId


class ContributorRepository(ABC):
    @abstractmethod
    async def save(self, contributor: Contributor) -> None: ...

    @abstractmethod
    async def get(self, contributor_id: ContributorId) -> Contributor | None: ...
