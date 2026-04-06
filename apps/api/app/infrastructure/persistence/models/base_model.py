from app.infrastructure.persistence.models.base import Base
from app.infrastructure.persistence.models.mixins.id import IDMixin
from app.infrastructure.persistence.models.mixins.timestamp import TimestampMixin


class BaseModel(IDMixin, TimestampMixin, Base):
    """Abstract SQLAlchemy base with `id`, `created_at`, and `updated_at` columns."""

    __abstract__ = True
