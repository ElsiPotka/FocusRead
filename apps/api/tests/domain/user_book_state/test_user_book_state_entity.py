from __future__ import annotations

from uuid import uuid4

from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.user_book_state.entities import UserBookState
from app.domain.user_book_state.value_objects import (
    PreferredWordsPerFlash,
    PreferredWPM,
)


def make_state(**kwargs) -> UserBookState:
    defaults = {
        "user_id": UserId(uuid4()),
        "book_id": BookId(uuid4()),
    }
    defaults.update(kwargs)
    return UserBookState.create(**defaults)


def test_create_defaults():
    state = make_state()
    assert state.favorited_at is None
    assert state.archived_at is None
    assert state.completed_at is None
    assert state.last_opened_at is None
    assert state.preferred_wpm is None
    assert state.preferred_words_per_flash is None
    assert state.skip_images is False
    assert state.ramp_up_enabled is True


def test_favorite_sets_timestamp():
    state = make_state()
    state.favorite()
    assert state.favorited_at is not None


def test_unfavorite_clears_timestamp():
    state = make_state()
    state.favorite()
    state.unfavorite()
    assert state.favorited_at is None


def test_favorite_idempotent():
    state = make_state()
    state.favorite()
    state.favorite()
    assert state.favorited_at is not None


def test_unfavorite_when_not_favorited():
    state = make_state()
    state.unfavorite()  # no-op, no error
    assert state.favorited_at is None


def test_archive_and_unarchive():
    state = make_state()
    state.archive()
    assert state.archived_at is not None
    state.unarchive()
    assert state.archived_at is None


def test_mark_completed_and_reopen():
    state = make_state()
    state.mark_completed()
    assert state.completed_at is not None
    state.reopen()
    assert state.completed_at is None


def test_record_opened():
    state = make_state()
    state.record_opened()
    assert state.last_opened_at is not None


def test_update_preferences():
    state = make_state()
    state.update_preferences(
        preferred_wpm=PreferredWPM(400),
        preferred_words_per_flash=PreferredWordsPerFlash(2),
        skip_images=True,
        ramp_up_enabled=False,
    )
    assert state.preferred_wpm is not None and state.preferred_wpm.value == 400
    assert state.preferred_words_per_flash is not None and state.preferred_words_per_flash.value == 2
    assert state.skip_images is True
    assert state.ramp_up_enabled is False


def test_update_preferences_partial():
    state = make_state()
    state.update_preferences(skip_images=True)
    assert state.skip_images is True
    assert state.ramp_up_enabled is True  # unchanged


def test_equality_by_composite_key():
    user_id = UserId(uuid4())
    book_id = BookId(uuid4())
    s1 = UserBookState.create(user_id=user_id, book_id=book_id)
    s2 = UserBookState.create(user_id=user_id, book_id=book_id)
    assert s1 == s2  # same user+book


def test_inequality_different_keys():
    s1 = make_state()
    s2 = make_state()
    assert s1 != s2
