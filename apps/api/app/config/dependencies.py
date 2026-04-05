from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.errors import ApplicationError
from app.config.db import get_db
from app.config.logger import log
from app.config.settings import settings
from app.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork, get_uow

DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
UnitOfWorkDep = Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]

__all__ = [
    "ApplicationError",
    "DatabaseSession",
    "UnitOfWorkDep",
    "get_db",
    "get_uow",
    "log",
    "settings",
]
