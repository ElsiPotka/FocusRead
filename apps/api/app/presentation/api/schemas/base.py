from pydantic import BaseModel, ConfigDict

from app.presentation.api.schemas.mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)


class BaseORMSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class BaseSchema(BaseORMSchema, UUIDMixin, TimestampMixin):
    pass


class SoftDeletableSchema(BaseSchema, SoftDeleteMixin):
    pass
