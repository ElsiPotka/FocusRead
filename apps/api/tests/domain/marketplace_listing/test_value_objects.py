from __future__ import annotations

import pytest

from app.domain.marketplace_listing.value_objects import (
    ListingSlug,
    ListingSourceRef,
    ListingStatus,
    ModerationStatus,
)


class TestListingSlug:
    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("deep-work", "deep-work"),
            ("  DEEP-WORK ", "deep-work"),
            ("a1b2c3", "a1b2c3"),
            ("one", "one"),
        ],
    )
    def test_normalizes(self, raw: str, expected: str):
        assert ListingSlug(raw).value == expected

    @pytest.mark.parametrize(
        "raw",
        [
            "",
            "   ",
            "-leading",
            "trailing-",
            "double--hyphen",
            "has space",
            "has_underscore",
            "punct!",
        ],
    )
    def test_rejects_invalid(self, raw: str):
        with pytest.raises(ValueError, match="Listing slug"):
            ListingSlug(raw)

    def test_rejects_too_long(self):
        with pytest.raises(ValueError, match="Listing slug"):
            ListingSlug("a" * 256)


class TestListingSourceRef:
    def test_strips(self):
        assert ListingSourceRef("  ext:abc ").value == "ext:abc"

    def test_rejects_blank(self):
        with pytest.raises(ValueError, match="Listing source ref"):
            ListingSourceRef("   ")

    def test_rejects_too_long(self):
        with pytest.raises(ValueError, match="Listing source ref"):
            ListingSourceRef("x" * 256)


class TestEnums:
    def test_listing_status_values(self):
        assert {s.value for s in ListingStatus} == {
            "draft",
            "published",
            "hidden",
            "archived",
        }

    def test_moderation_status_values(self):
        assert {m.value for m in ModerationStatus} == {
            "pending",
            "approved",
            "rejected",
        }
