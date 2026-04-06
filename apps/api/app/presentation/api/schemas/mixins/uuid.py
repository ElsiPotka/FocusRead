from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    import uuid


class UUIDMixin(BaseModel):
    id: uuid.UUID = Field(..., description="Unique identifier (UUIDv7)")
