from __future__ import annotations

import pytest

from app.domain.book_chunks.value_objects import (
    ChunkIndex,
    ChunkWordCount,
    ChunkWordData,
    StartWordIndex,
)


class TestChunkIndex:
    def test_accepts_zero(self):
        assert ChunkIndex(0).value == 0

    def test_accepts_positive(self):
        assert ChunkIndex(5).value == 5

    def test_rejects_negative(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            ChunkIndex(-1)


class TestStartWordIndex:
    def test_accepts_zero(self):
        assert StartWordIndex(0).value == 0

    def test_accepts_positive(self):
        assert StartWordIndex(100).value == 100

    def test_rejects_negative(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            StartWordIndex(-1)


class TestChunkWordCount:
    def test_accepts_positive(self):
        assert ChunkWordCount(1).value == 1

    def test_rejects_zero(self):
        with pytest.raises(ValueError, match="greater than zero"):
            ChunkWordCount(0)

    def test_rejects_negative(self):
        with pytest.raises(ValueError, match="greater than zero"):
            ChunkWordCount(-1)


class TestChunkWordData:
    def test_accepts_non_empty(self):
        data = [["w", "hello", 1.0]]
        assert ChunkWordData(data).value == data

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            ChunkWordData([])
