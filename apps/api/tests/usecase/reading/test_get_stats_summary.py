from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.common.unit_of_work import AbstractUnitOfWork
from app.application.reading.use_cases.get_stats_summary import GetStatsSummary
from app.domain.library_item.value_objects import LibraryItemId
from app.domain.reading_stats.entities import ReadingStat
from app.domain.reading_stats.repositories import ReadingStatRepository
from app.domain.reading_stats.value_objects import (
    SessionDate,
)


@pytest.fixture
def stat_repo():
    return AsyncMock(spec=ReadingStatRepository)


@pytest.fixture
def uow(stat_repo):
    mock = AsyncMock(spec=AbstractUnitOfWork)
    mock.reading_stats = stat_repo
    return mock


def make_stat(library_item_id, session_date, words, time_sec):
    stat = ReadingStat.create(
        library_item_id=LibraryItemId(library_item_id),
        session_date=SessionDate(session_date),
    )
    if words > 0 or time_sec > 0:
        stat.record_activity(words_read_delta=words, time_spent_delta_sec=time_sec)
    return stat


async def test_empty_stats(uow, stat_repo):
    stat_repo.list_for_user.return_value = []

    summary = await GetStatsSummary(uow).execute(user_id=uuid4())

    assert summary.total_words_read == 0
    assert summary.total_time_spent_sec == 0
    assert summary.books_read_count == 0
    assert summary.daily_stats == []


async def test_aggregates_across_books(uow, stat_repo):
    item1 = uuid4()
    item2 = uuid4()
    today = date.today()

    stats = [
        make_stat(item1, today, 300, 30),
        make_stat(item2, today, 200, 20),
    ]
    stat_repo.list_for_user.return_value = stats

    summary = await GetStatsSummary(uow).execute(user_id=uuid4())

    assert summary.total_words_read == 500
    assert summary.total_time_spent_sec == 50
    assert summary.books_read_count == 2


async def test_daily_stats_grouped_by_date(uow, stat_repo):
    item_id = uuid4()
    today = date.today()
    yesterday = today - timedelta(days=1)

    stats = [
        make_stat(item_id, today, 300, 30),
        make_stat(item_id, yesterday, 200, 20),
    ]
    stat_repo.list_for_user.return_value = stats

    summary = await GetStatsSummary(uow).execute(user_id=uuid4())

    assert len(summary.daily_stats) == 2
    assert summary.daily_stats[0].date == today
    assert summary.daily_stats[0].words_read == 300


async def test_since_filter_passed_to_repo(uow, stat_repo):
    stat_repo.list_for_user.return_value = []
    since = date.today() - timedelta(days=7)

    await GetStatsSummary(uow).execute(user_id=uuid4(), since=since)

    call_kwargs = stat_repo.list_for_user.call_args.kwargs
    assert call_kwargs["since"] == since
