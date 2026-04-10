from __future__ import annotations

import pytest

from app.domain.shelf.value_objects import (
    ShelfColor,
    ShelfDescription,
    ShelfIcon,
    ShelfName,
)


class TestShelfName:
    def test_valid(self):
        assert ShelfName("Fiction").value == "Fiction"

    def test_strips_whitespace(self):
        assert ShelfName("  Fiction  ").value == "Fiction"

    def test_blank_raises(self):
        with pytest.raises(ValueError, match="required"):
            ShelfName("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="required"):
            ShelfName("   ")

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="255"):
            ShelfName("x" * 256)


class TestShelfDescription:
    def test_valid(self):
        assert ShelfDescription("My books").value == "My books"

    def test_blank_raises(self):
        with pytest.raises(ValueError, match="blank"):
            ShelfDescription("")

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="1000"):
            ShelfDescription("x" * 1001)


class TestShelfColor:
    def test_valid(self):
        assert ShelfColor("#ff0000").value == "#ff0000"

    def test_blank_raises(self):
        with pytest.raises(ValueError, match="blank"):
            ShelfColor("")

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="32"):
            ShelfColor("x" * 33)


class TestShelfIcon:
    def test_valid(self):
        assert ShelfIcon("book").value == "book"

    def test_blank_raises(self):
        with pytest.raises(ValueError, match="blank"):
            ShelfIcon("")

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="64"):
            ShelfIcon("x" * 65)
