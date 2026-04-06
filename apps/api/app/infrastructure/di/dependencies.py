from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.errors import ApplicationError
from app.infrastructure.cache.redis import RedisCache, RedisClient, get_cache, get_redis
from app.infrastructure.config.settings import settings
from app.infrastructure.logging.logger import log
from app.infrastructure.persistence.db import get_db
from app.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork, get_uow

DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
UnitOfWorkDep = Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]
CacheDep = Annotated[RedisCache, Depends(get_cache)]

__all__ = [
    "ApplicationError",
    "CacheDep",
    "DatabaseSession",
    "RedisClient",
    "UnitOfWorkDep",
    "get_cache",
    "get_db",
    "get_redis",
    "get_uow",
    "log",
    "settings",
]
