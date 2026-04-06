from __future__ import annotations

from uuid import UUID

import pytest

from app.domain.auth.value_objects import (
    AccountId,
    Email,
    HashedPassword,
    ProviderId,
    RawPassword,
    RefreshTokenHash,
    UserId,
)


class TestUserId:
    def test_generate_creates_valid_uuid(self):
        uid = UserId.generate()
        assert isinstance(uid.value, UUID)

    def test_two_generated_ids_are_different(self):
        assert UserId.generate() != UserId.generate()

    def test_str_returns_uuid_string(self):
        uid = UserId.generate()
        assert str(uid) == str(uid.value)

    def test_equality_by_value(self):
        raw = UUID("01234567-89ab-cdef-0123-456789abcdef")
        assert UserId(raw) == UserId(raw)

    def test_frozen(self):
        uid = UserId.generate()
        attribute_name = "value"
        with pytest.raises(AttributeError):
            setattr(uid, attribute_name, UUID("01234567-89ab-cdef-0123-456789abcdef"))


class TestEmail:
    def test_normalizes_to_lowercase(self):
        assert Email("User@Example.COM").value == "user@example.com"

    def test_strips_whitespace(self):
        assert Email("  user@example.com  ").value == "user@example.com"

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="Email is required"):
            Email("")

    def test_rejects_whitespace_only(self):
        with pytest.raises(ValueError, match="Email is required"):
            Email("   ")

    def test_rejects_too_long(self):
        with pytest.raises(ValueError, match="320 characters"):
            Email("a" * 310 + "@example.com")

    def test_rejects_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("not-an-email")

    def test_accepts_valid_email(self):
        email = Email("hello@world.co")
        assert email.value == "hello@world.co"


class TestHashedPassword:
    def test_accepts_non_empty(self):
        hp = HashedPassword("$argon2id$hash")
        assert hp.value == "$argon2id$hash"

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            HashedPassword("")


class TestRawPassword:
    def test_accepts_valid_length(self):
        pw = RawPassword("a" * 8)
        assert pw.value == "a" * 8

    def test_rejects_too_short(self):
        with pytest.raises(ValueError, match="at least 8"):
            RawPassword("short")

    def test_rejects_too_long(self):
        with pytest.raises(ValueError, match="128 characters"):
            RawPassword("a" * 129)

    def test_boundary_8_chars(self):
        assert RawPassword("12345678").value == "12345678"

    def test_boundary_128_chars(self):
        assert RawPassword("x" * 128).value == "x" * 128


class TestRefreshTokenHash:
    def test_accepts_64_char_hex(self):
        valid = "a" * 64
        assert RefreshTokenHash(valid).value == valid

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="Invalid refresh token hash"):
            RefreshTokenHash("")

    def test_rejects_wrong_length(self):
        with pytest.raises(ValueError, match="Invalid refresh token hash"):
            RefreshTokenHash("abc123")


class TestProviderId:
    @pytest.mark.parametrize("provider", ["credential", "google", "apple"])
    def test_accepts_valid_providers(self, provider):
        assert ProviderId(provider).value == provider

    def test_rejects_unknown_provider(self):
        with pytest.raises(ValueError, match="Invalid provider"):
            ProviderId("facebook")


class TestAccountId:
    def test_accepts_non_empty(self):
        assert AccountId("google-sub-123").value == "google-sub-123"

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="Account ID is required"):
            AccountId("")

    def test_rejects_whitespace_only(self):
        with pytest.raises(ValueError, match="Account ID is required"):
            AccountId("   ")
