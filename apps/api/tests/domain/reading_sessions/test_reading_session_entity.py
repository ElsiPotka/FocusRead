from __future__ import annotations

from uuid import uuid4

from app.domain.library_item.value_objects import LibraryItemId
from app.domain.reading_sessions.entities import ReadingSession
from app.domain.reading_sessions.value_objects import (
    CurrentChunk,
    CurrentWordIndex,
    WordsPerFlash,
    WpmSpeed,
)


def make_session(
    *,
    library_item_id: LibraryItemId | None = None,
    wpm_speed: WpmSpeed | None = None,
    words_per_flash: WordsPerFlash | None = None,
) -> ReadingSession:
    return ReadingSession.create(
        library_item_id=library_item_id or LibraryItemId(uuid4()),
        wpm_speed=wpm_speed,
        words_per_flash=words_per_flash,
    )


def test_create_defaults():
    session = make_session()
    assert session.current_word_index.value == 0
    assert session.current_chunk.value == 0
    assert session.wpm_speed.value == 250
    assert session.words_per_flash.value == 1


def test_create_with_custom_settings():
    session = make_session(
        wpm_speed=WpmSpeed(400),
        words_per_flash=WordsPerFlash(2),
    )
    assert session.wpm_speed.value == 400
    assert session.words_per_flash.value == 2


def test_update_progress_changes_position():
    session = make_session()
    session.update_progress(
        current_word_index=CurrentWordIndex(1500),
        current_chunk=CurrentChunk(1),
    )
    assert session.current_word_index.value == 1500
    assert session.current_chunk.value == 1


def test_update_progress_updates_wpm():
    session = make_session()
    session.update_progress(
        current_word_index=CurrentWordIndex(100),
        current_chunk=CurrentChunk(0),
        wpm_speed=WpmSpeed(600),
    )
    assert session.wpm_speed.value == 600


def test_update_progress_stamps_last_read_at():
    session = make_session()
    before = session.last_read_at
    session.update_progress(
        current_word_index=CurrentWordIndex(50),
        current_chunk=CurrentChunk(0),
    )
    assert session.last_read_at >= before


def test_equality_by_id():
    s1 = make_session()
    s2 = make_session()
    assert s1 != s2
    assert s1 == s1
