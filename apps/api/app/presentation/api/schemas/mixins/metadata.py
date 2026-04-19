from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.types import JSONObject


class MetadataMixin(BaseModel):
    """Exposes arbitrary JSON metadata on API schemas."""

    entity_metadata: JSONObject | None = Field(
        default=None, description="Flexible JSON metadata"
    )
