from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.domain.auth.value_objects import RefreshTokenHash, UserId
from app.domain.session.entities import Session


def _valid_hash(char: str = "a") -> RefreshTokenHash:
    return RefreshTokenHash(char * 64)


class TestSessionCreate:
    def test_create_sets_fields(self):
        user_id = UserId.generate()
        expires = datetime.now(UTC) + timedelta(days=7)
        token_hash = _valid_hash()

        session = Session.create(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires,
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1",
        )

        assert session.user_id == user_id
        assert session.token_hash == token_hash
        assert session.expires_at == expires
        assert session.user_agent == "Mozilla/5.0"
        assert session.ip_address == "127.0.0.1"

    def test_create_generates_unique_id(self):
        expires = datetime.now(UTC) + timedelta(days=7)
        s1 = Session.create(
            user_id=UserId.generate(),
            token_hash=_valid_hash("a"),
            expires_at=expires,
        )
        s2 = Session.create(
            user_id=UserId.generate(),
            token_hash=_valid_hash("b"),
            expires_at=expires,
        )
        assert s1.id != s2.id

    def test_optional_fields_default_to_none(self):
        session = Session.create(
            user_id=UserId.generate(),
            token_hash=_valid_hash(),
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        assert session.user_agent is None
        assert session.ip_address is None


class TestSessionIsExpired:
    def test_not_expired_when_future(self):
        session = Session.create(
            user_id=UserId.generate(),
            token_hash=_valid_hash(),
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        assert session.is_expired is False

    def test_expired_when_past(self):
        session = Session.create(
            user_id=UserId.generate(),
            token_hash=_valid_hash(),
            expires_at=datetime.now(UTC) - timedelta(seconds=1),
        )
        assert session.is_expired is True


class TestSessionRotate:
    def test_rotate_updates_hash_and_expiry(self):
        old_hash = _valid_hash("a")
        new_hash = _valid_hash("b")
        old_expires = datetime.now(UTC) + timedelta(days=7)
        new_expires = datetime.now(UTC) + timedelta(days=14)

        session = Session.create(
            user_id=UserId.generate(),
            token_hash=old_hash,
            expires_at=old_expires,
        )
        original_updated = session.updated_at

        session.rotate(new_hash, new_expires)

        assert session.token_hash == new_hash
        assert session.expires_at == new_expires
        assert session.updated_at >= original_updated

    def test_rotate_preserves_id_and_user(self):
        user_id = UserId.generate()
        session = Session.create(
            user_id=user_id,
            token_hash=_valid_hash("a"),
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        session_id = session.id

        session.rotate(_valid_hash("b"), datetime.now(UTC) + timedelta(days=14))

        assert session.id == session_id
        assert session.user_id == user_id


class TestSessionEquality:
    def test_same_id_equal(self):
        uid = UserId.generate()
        s1 = Session(
            id=uid,
            user_id=UserId.generate(),
            token_hash=_valid_hash("a"),
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        s2 = Session(
            id=uid,
            user_id=UserId.generate(),
            token_hash=_valid_hash("b"),
            expires_at=datetime.now(UTC) + timedelta(days=14),
        )
        assert s1 == s2

    def test_different_id_not_equal(self):
        expires = datetime.now(UTC) + timedelta(days=7)
        s1 = Session.create(
            user_id=UserId.generate(), token_hash=_valid_hash(), expires_at=expires
        )
        s2 = Session.create(
            user_id=UserId.generate(), token_hash=_valid_hash(), expires_at=expires
        )
        assert s1 != s2
