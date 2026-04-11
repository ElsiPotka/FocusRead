from __future__ import annotations

from uuid import uuid4

import pytest

from app.domain.auth.value_objects import UserId
from app.domain.books.filter import BookFilter, BookSortField, SortDirection


class TestBookFilter:
    def test_defaults(self):
        uid = UserId(uuid4())
        f = BookFilter(owner_user_id=uid)

        assert f.owner_user_id == uid
        assert f.query is None
        assert f.favorited is None
        assert f.archived is None
        assert f.completed is None
        assert f.continue_reading is None
        assert f.document_type is None
        assert f.status is None
        assert f.sort_by == BookSortField.CREATED_AT
        assert f.sort_dir == SortDirection.DESC
        assert f.limit is None
        assert f.offset == 0

    def test_all_fields(self):
        uid = UserId(uuid4())
        f = BookFilter(
            owner_user_id=uid,
            query="deep work",
            favorited=True,
            archived=False,
            completed=None,
            continue_reading=True,
            document_type="book",
            status="ready",
            sort_by=BookSortField.TITLE,
            sort_dir=SortDirection.ASC,
            limit=20,
            offset=10,
        )

        assert f.query == "deep work"
        assert f.favorited is True
        assert f.archived is False
        assert f.completed is None
        assert f.continue_reading is True
        assert f.document_type == "book"
        assert f.status == "ready"
        assert f.sort_by == BookSortField.TITLE
        assert f.sort_dir == SortDirection.ASC
        assert f.limit == 20
        assert f.offset == 10

    def test_frozen(self):
        f = BookFilter(owner_user_id=UserId(uuid4()))
        with pytest.raises(AttributeError):
            f.query = "test"  # type: ignore[misc]
