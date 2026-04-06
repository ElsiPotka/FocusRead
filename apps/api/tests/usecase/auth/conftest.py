from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from app.application.common.unit_of_work import AbstractUnitOfWork
from app.domain.auth.repositories import (
    AccountRepository,
    JWTSigningKeyRepository,
    SessionRepository,
    UserRepository,
)
from app.infrastructure.auth.jwt_service import JWTService
from app.infrastructure.auth.session_service import SessionService


@pytest.fixture
def user_repo():
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def account_repo():
    return AsyncMock(spec=AccountRepository)


@pytest.fixture
def session_repo():
    return AsyncMock(spec=SessionRepository)


@pytest.fixture
def jwt_signing_key_repo():
    return AsyncMock(spec=JWTSigningKeyRepository)


@pytest.fixture
def uow(user_repo, account_repo, session_repo, jwt_signing_key_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.users = user_repo
    mock.accounts = account_repo
    mock.sessions = session_repo
    mock.jwt_signing_keys = jwt_signing_key_repo
    return mock


@pytest.fixture
def jwt_service():
    svc = AsyncMock(spec=JWTService)
    svc.get_or_create_key_pair.return_value = ("private_pem", "public_pem")
    svc.encode_access_token.return_value = "access_token_xxx"
    return svc


@pytest.fixture
def session_service():
    svc = AsyncMock(spec=SessionService)
    svc.generate_refresh_token.return_value = "raw_refresh_token_xxx"
    svc.hash_token.return_value = "a" * 64
    return svc
