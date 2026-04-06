from app.infrastructure.persistence.models.base import Base
from app.infrastructure.persistence.models.mixins.timestamp import TimestampMixin
from app.infrastructure.persistence.models.mixins.uuid import UUIDMixin


class BaseModel(UUIDMixin, TimestampMixin, Base):
    __abstract__ = True
