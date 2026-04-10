from __future__ import annotations

import pytest

from app.domain.label.value_objects import LabelColor, LabelName, LabelSlug


class TestLabelName:
    def test_valid(self):
        assert LabelName("Fiction").value == "Fiction"

    def test_strips_whitespace(self):
        assert LabelName("  Fiction  ").value == "Fiction"

    def test_blank_raises(self):
        with pytest.raises(ValueError, match="required"):
            LabelName("")

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="255"):
            LabelName("x" * 256)


class TestLabelSlug:
    def test_valid(self):
        assert LabelSlug("fiction").value == "fiction"

    def test_lowercases(self):
        assert LabelSlug("Fiction").value == "fiction"

    def test_strips_whitespace(self):
        assert LabelSlug("  fiction  ").value == "fiction"

    def test_blank_raises(self):
        with pytest.raises(ValueError, match="required"):
            LabelSlug("")

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="255"):
            LabelSlug("x" * 256)


class TestLabelColor:
    def test_valid(self):
        assert LabelColor("#ff0000").value == "#ff0000"

    def test_blank_raises(self):
        with pytest.raises(ValueError, match="blank"):
            LabelColor("")

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="32"):
            LabelColor("x" * 33)
