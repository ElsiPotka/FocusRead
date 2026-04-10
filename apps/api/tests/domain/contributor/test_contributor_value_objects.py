from __future__ import annotations

import pytest

from app.domain.contributor.value_objects import (
    ContributorDisplayName,
    ContributorRole,
    ContributorSortName,
)


class TestContributorDisplayName:
    def test_valid_name(self):
        name = ContributorDisplayName("Jane Doe")
        assert name.value == "Jane Doe"

    def test_strips_whitespace(self):
        name = ContributorDisplayName("  Jane Doe  ")
        assert name.value == "Jane Doe"

    def test_blank_raises(self):
        with pytest.raises(ValueError, match="required"):
            ContributorDisplayName("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="required"):
            ContributorDisplayName("   ")

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="255 characters"):
            ContributorDisplayName("x" * 256)

    def test_max_length_ok(self):
        name = ContributorDisplayName("x" * 255)
        assert len(name.value) == 255


class TestContributorSortName:
    def test_valid_name(self):
        name = ContributorSortName("Doe, Jane")
        assert name.value == "Doe, Jane"

    def test_strips_whitespace(self):
        name = ContributorSortName("  Doe, Jane  ")
        assert name.value == "Doe, Jane"

    def test_blank_raises(self):
        with pytest.raises(ValueError, match="cannot be blank"):
            ContributorSortName("")

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="255 characters"):
            ContributorSortName("x" * 256)


class TestContributorRole:
    def test_all_roles(self):
        assert ContributorRole.AUTHOR == "author"
        assert ContributorRole.EDITOR == "editor"
        assert ContributorRole.TRANSLATOR == "translator"
        assert ContributorRole.ILLUSTRATOR == "illustrator"
        assert ContributorRole.OTHER == "other"

    def test_from_string(self):
        role = ContributorRole("author")
        assert role is ContributorRole.AUTHOR

    def test_invalid_role_raises(self):
        with pytest.raises(ValueError):
            ContributorRole("invalid")
