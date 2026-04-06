from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.label.entities import Label
    from app.domain.label.value_objects import LabelId


class LabelRepository(ABC):
    @abstractmethod
    async def save(self, label: Label) -> None: ...

    @abstractmethod
    async def get(self, label_id: LabelId) -> Label | None: ...
