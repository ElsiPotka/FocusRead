from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.security import SecurityScopes  # noqa: TC002
from fastapi.testclient import TestClient

from app.application.common.errors import ApplicationError
from app.domain.auth.value_objects import Email, UserId
from app.domain.role.entities import Role
from app.domain.role.value_objects import RoleName
from app.domain.user.entities import User
from app.infrastructure.config.settings import settings
from app.infrastructure.persistence.unit_of_work import get_uow
from app.presentation.api.exception_handlers import register_exception_handlers
from app.presentation.api.middleware.auth import get_current_user
from app.presentation.api.routers.admin import router as admin_router


def _build_user() -> User:
    return User(
        id=UserId(uuid4()),
        name="Admin",
        surname="User",
        email=Email("admin@example.com"),
        email_verified=True,
        is_active=True,
    )


def _build_role(name: RoleName) -> Role:
    return Role.create(name=name, description=f"{name.value} access")


def _build_uow(*, resolved_roles: list[Role], assigned_roles: list[Role]):
    users = SimpleNamespace(get=AsyncMock(return_value=_build_user()))
    roles = SimpleNamespace(
        get_by_names=AsyncMock(return_value=resolved_roles),
        assign_many_to_user=AsyncMock(),
        remove_many_from_user=AsyncMock(),
        list_for_user=AsyncMock(return_value=assigned_roles),
    )
    return SimpleNamespace(users=users, roles=roles, commit=AsyncMock())


def _create_client(*, user_scopes: set[str], uow) -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(admin_router, prefix=settings.API_V1_PREFIX)

    async def fake_get_current_user(security_scopes: SecurityScopes) -> User:
        for scope in security_scopes.scopes:
            if scope not in user_scopes:
                raise ApplicationError("Not enough permissions", status_code=403)
        return _build_user()

    app.dependency_overrides[get_current_user] = fake_get_current_user
    app.dependency_overrides[get_uow] = lambda: uow
    return TestClient(app)


class TestAdminRoleRoutes:
    @pytest.mark.parametrize("method", ["put", "delete"])
    def test_forbids_non_admin_users(self, method: str):
        user_id = uuid4()
        client = _create_client(
            user_scopes={RoleName.CLIENT.value},
            uow=_build_uow(resolved_roles=[], assigned_roles=[]),
        )

        response = client.request(
            method,
            f"{settings.API_V1_PREFIX}/admin/users/{user_id}/roles",
            json={"roles": [RoleName.MERCHANT.value]},
        )

        assert response.status_code == 403
        assert response.json() == {
            "success": False,
            "message": "Not enough permissions",
        }

    def test_allows_admin_to_assign_roles(self):
        user_id = uuid4()
        merchant_role = _build_role(RoleName.MERCHANT)
        uow = _build_uow(
            resolved_roles=[merchant_role],
            assigned_roles=[merchant_role],
        )
        client = _create_client(user_scopes={RoleName.ADMIN.value}, uow=uow)

        response = client.put(
            f"{settings.API_V1_PREFIX}/admin/users/{user_id}/roles",
            json={"roles": [RoleName.MERCHANT.value]},
        )

        assert response.status_code == 200
        assert response.json() == {
            "success": True,
            "message": "Roles assigned",
            "data": {
                "user_id": str(user_id),
                "roles": [
                    {
                        "id": str(merchant_role.id.value),
                        "name": RoleName.MERCHANT.value,
                        "description": merchant_role.description,
                    }
                ],
            },
        }
        uow.roles.assign_many_to_user.assert_awaited_once_with(
            UserId(user_id),
            [merchant_role.id],
        )
        uow.commit.assert_awaited_once()

    def test_allows_admin_to_remove_roles(self):
        user_id = uuid4()
        client_role = _build_role(RoleName.CLIENT)
        uow = _build_uow(
            resolved_roles=[client_role],
            assigned_roles=[],
        )
        client = _create_client(user_scopes={RoleName.ADMIN.value}, uow=uow)

        response = client.request(
            "delete",
            f"{settings.API_V1_PREFIX}/admin/users/{user_id}/roles",
            json={"roles": [RoleName.CLIENT.value]},
        )

        assert response.status_code == 200
        assert response.json() == {
            "success": True,
            "message": "Roles removed",
            "data": {
                "user_id": str(user_id),
                "roles": [],
            },
        }
        uow.roles.remove_many_from_user.assert_awaited_once_with(
            UserId(user_id),
            [client_role.id],
        )
        uow.commit.assert_awaited_once()
