from __future__ import annotations

import inspect

from fastapi.params import Security as SecurityParam

from app.domain.auth.value_objects import Email
from app.domain.role.value_objects import RoleName
from app.domain.user.entities import User
from app.presentation.api.middleware.auth import role_guard


class TestRoleGuard:
    async def test_returns_current_user(self):
        user = User.create(
            name="Admin", surname="User", email=Email("admin@example.com")
        )

        guard = role_guard(RoleName.ADMIN)

        assert await guard(user) == user

    def test_binds_required_scope(self):
        guard = role_guard(RoleName.ADMIN)
        current_user_param = inspect.signature(guard).parameters["current_user"]

        assert isinstance(current_user_param.default, SecurityParam)
        assert current_user_param.default.scopes == [RoleName.ADMIN.value]
