from pydantic import BaseModel, Field


class TagsMixin(BaseModel):
    tags: list[str] | None = Field(default=None, description="Array of tags")
