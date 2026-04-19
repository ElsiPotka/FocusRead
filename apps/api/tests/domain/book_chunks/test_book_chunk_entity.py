from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest

from app.domain.book_asset.value_objects import BookAssetId
from app.domain.book_chunks.entities import BookChunk
from app.domain.book_chunks.value_objects import (
    ChunkIndex,
    ChunkWordCount,
    ChunkWordData,
    StartWordIndex,
)


class TestBookChunk:
    def test_create_sets_expected_defaults(self):
        book_asset_id = BookAssetId(uuid4())
        word_data = ChunkWordData([["w", "hello", 1.0], ["w", "world.", 2.0]])

        chunk = BookChunk.create(
            book_asset_id=book_asset_id,
            chunk_index=ChunkIndex(0),
            start_word_index=StartWordIndex(0),
            word_data=word_data,
            word_count=ChunkWordCount(2),
            page_start=1,
            page_end=3,
        )

        assert chunk.book_asset_id == book_asset_id
        assert chunk.chunk_index.value == 0
        assert chunk.start_word_index.value == 0
        assert chunk.word_count.value == 2
        assert len(chunk.word_data.value) == 2
        assert chunk.page_start == 1
        assert chunk.page_end == 3
        assert isinstance(chunk.created_at, datetime)
        assert isinstance(chunk.updated_at, datetime)

    def test_create_without_page_range(self):
        chunk = BookChunk.create(
            book_asset_id=BookAssetId(uuid4()),
            chunk_index=ChunkIndex(0),
            start_word_index=StartWordIndex(0),
            word_data=ChunkWordData([["w", "test", 1.0]]),
            word_count=ChunkWordCount(1),
        )

        assert chunk.page_start is None
        assert chunk.page_end is None

    def test_rejects_non_positive_page_start(self):
        with pytest.raises(ValueError, match="Page start must be positive"):
            BookChunk.create(
                book_asset_id=BookAssetId(uuid4()),
                chunk_index=ChunkIndex(0),
                start_word_index=StartWordIndex(0),
                word_data=ChunkWordData([["w", "test", 1.0]]),
                word_count=ChunkWordCount(1),
                page_start=0,
            )

    def test_rejects_non_positive_page_end(self):
        with pytest.raises(ValueError, match="Page end must be positive"):
            BookChunk.create(
                book_asset_id=BookAssetId(uuid4()),
                chunk_index=ChunkIndex(0),
                start_word_index=StartWordIndex(0),
                word_data=ChunkWordData([["w", "test", 1.0]]),
                word_count=ChunkWordCount(1),
                page_end=0,
            )

    def test_equality_by_id(self):
        chunk1 = BookChunk.create(
            book_asset_id=BookAssetId(uuid4()),
            chunk_index=ChunkIndex(0),
            start_word_index=StartWordIndex(0),
            word_data=ChunkWordData([["w", "test", 1.0]]),
            word_count=ChunkWordCount(1),
        )
        chunk2 = BookChunk.create(
            book_asset_id=BookAssetId(uuid4()),
            chunk_index=ChunkIndex(0),
            start_word_index=StartWordIndex(0),
            word_data=ChunkWordData([["w", "test", 1.0]]),
            word_count=ChunkWordCount(1),
        )

        assert chunk1 != chunk2
        assert chunk1 == chunk1
