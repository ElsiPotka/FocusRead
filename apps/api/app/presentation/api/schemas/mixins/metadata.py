from typing import Any

from pydantic import BaseModel, Field


class MetadataMixin(BaseModel):
    entity_metadata: dict[str, Any] | None = Field(
        default=None, description="Flexible JSON metadata"
    )
