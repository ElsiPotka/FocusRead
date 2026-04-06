from pydantic import BaseModel, Field


class VersionMixin(BaseModel):
    version: int = Field(default=1, description="Version for optimistic locking")
