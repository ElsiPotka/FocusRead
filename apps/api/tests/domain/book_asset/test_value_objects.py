from __future__ import annotations

import pytest

from app.domain.book_asset.value_objects import (
    FileSizeBytes,
    MimeType,
    OriginalFilename,
    PageCount,
    ProcessingError,
    Sha256,
    StorageKey,
    TotalChunks,
    WordCount,
)


class TestSha256:
    def test_accepts_valid_lowercase_hex(self):
        raw = "a" * 64
        assert Sha256(raw).value == raw

    def test_normalizes_uppercase_hex(self):
        assert Sha256("A" * 64).value == "a" * 64

    def test_strips_whitespace(self):
        raw = "a" * 64
        assert Sha256(f"  {raw}  ").value == raw

    @pytest.mark.parametrize(
        "value",
        ["", "short", "g" * 64, "a" * 63, "a" * 65],
    )
    def test_rejects_invalid(self, value: str):
        with pytest.raises(ValueError, match="Sha256"):
            Sha256(value)


class TestFileSizeBytes:
    def test_positive_size(self):
        assert FileSizeBytes(1).value == 1

    @pytest.mark.parametrize("value", [0, -1])
    def test_rejects_non_positive(self, value: int):
        with pytest.raises(ValueError, match="File size"):
            FileSizeBytes(value)


class TestMimeType:
    def test_normalizes_case(self):
        assert MimeType("Application/PDF").value == "application/pdf"

    def test_rejects_blank(self):
        with pytest.raises(ValueError, match="Mime type"):
            MimeType("  ")


class TestStorageKey:
    def test_accepts_content_addressed_key(self):
        key = "books/sha256/ab/cd/" + ("a" * 64) + ".pdf"
        assert StorageKey(key).value == key

    def test_rejects_blank(self):
        with pytest.raises(ValueError, match="Storage key"):
            StorageKey("  ")


class TestOriginalFilename:
    def test_strips(self):
        assert OriginalFilename("  book.pdf ").value == "book.pdf"

    def test_rejects_blank(self):
        with pytest.raises(ValueError, match="Original filename"):
            OriginalFilename("   ")


class TestProcessingError:
    def test_accepts(self):
        assert ProcessingError("boom").value == "boom"

    def test_rejects_blank(self):
        with pytest.raises(ValueError, match="Processing error"):
            ProcessingError("   ")


class TestPageCount:
    @pytest.mark.parametrize("value", [0, -1])
    def test_rejects_non_positive(self, value: int):
        with pytest.raises(ValueError, match="Page count"):
            PageCount(value)


class TestWordCount:
    def test_accepts_zero(self):
        assert WordCount(0).value == 0

    def test_rejects_negative(self):
        with pytest.raises(ValueError, match="Word count"):
            WordCount(-1)


class TestTotalChunks:
    def test_accepts_zero(self):
        assert TotalChunks(0).value == 0

    def test_rejects_negative(self):
        with pytest.raises(ValueError, match="Total chunks"):
            TotalChunks(-1)
