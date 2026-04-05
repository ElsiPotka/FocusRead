from app.shared.models.base import Base
from app.shared.models.mixins.timestamp import TimestampMixin
from app.shared.models.mixins.uuid import UUIDMixin


class BaseModel(UUIDMixin, TimestampMixin, Base):
    __abstract__ = True
