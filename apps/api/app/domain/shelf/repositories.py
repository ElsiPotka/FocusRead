from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.shelf.entities import Shelf
    from app.domain.shelf.value_objects import ShelfId


class ShelfRepository(ABC):
    @abstractmethod
    async def save(self, shelf: Shelf) -> None: ...

    @abstractmethod
    async def get(self, shelf_id: ShelfId) -> Shelf | None: ...
