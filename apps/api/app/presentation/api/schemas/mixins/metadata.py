from typing import Any

from pydantic import BaseModel, Field


class MetadataMixin(BaseModel):
    """Exposes arbitrary JSON metadata on API schemas."""

    entity_metadata: dict[str, Any] | None = Field(
        default=None, description="Flexible JSON metadata"
    )
