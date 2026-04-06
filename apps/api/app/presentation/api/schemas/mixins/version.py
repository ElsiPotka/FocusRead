from pydantic import BaseModel, Field


class VersionMixin(BaseModel):
    """Exposes the optimistic-lock version number on API schemas."""

    version: int = Field(default=1, description="Version for optimistic locking")
