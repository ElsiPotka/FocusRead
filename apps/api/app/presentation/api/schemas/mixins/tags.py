from pydantic import BaseModel, Field


class TagsMixin(BaseModel):
    """Exposes a list of tags on API schemas."""

    tags: list[str] | None = Field(default=None, description="Array of tags")
