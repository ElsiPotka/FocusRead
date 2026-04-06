from __future__ import annotations

from app.application.admin.list_users import ListUsersForAdmin


class TestListUsersForAdmin:
    async def test_returns_paginated_profiles(self, uow):
        page = {
            "items": [],
            "meta": {
                "page": 1,
                "per_page": 20,
                "total": 0,
                "total_pages": 0,
                "has_next": False,
                "has_prev": False,
                "next_cursor": None,
                "prev_cursor": None,
            },
        }
        uow.users.paginate_profiles.return_value = page

        result = await ListUsersForAdmin(uow).execute(page=1, per_page=20)

        assert result == page
        uow.users.paginate_profiles.assert_called_once_with(
            page=1,
            per_page=20,
            cursor=None,
        )
