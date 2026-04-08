"""
PDF processing pipeline using PyMuPDF (fitz).

Extracts text from PDF pages, tokenizes it, and yields chunks of ~2500 words
aligned to page boundaries when possible.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import fitz

from app.workers.tokenizer import make_image_token, tokenize_text

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass
class RawChunk:
    tokens: list[list]
    word_count: int
    page_start: int
    page_end: int
    has_images: bool = False


@dataclass
class _ChunkAccumulator:
    tokens: list[list] = field(default_factory=list)
    word_count: int = 0
    page_start: int = 0
    page_end: int = 0
    has_images: bool = False

    def add_tokens(self, new_tokens: list[list], page_num: int) -> None:
        if not self.tokens:
            self.page_start = page_num
        self.page_end = page_num
        for token in new_tokens:
            self.tokens.append(token)
            if token[0] == "w":
                self.word_count += 1
            elif token[0] == "i":
                self.has_images = True

    def to_chunk(self) -> RawChunk:
        return RawChunk(
            tokens=self.tokens,
            word_count=self.word_count,
            page_start=self.page_start,
            page_end=self.page_end,
            has_images=self.has_images,
        )

    def reset(self) -> None:
        self.tokens = []
        self.word_count = 0
        self.page_start = 0
        self.page_end = 0
        self.has_images = False

    @property
    def serialized_size(self) -> int:
        return len(json.dumps(self.tokens, ensure_ascii=False, separators=(",", ":")))


class PDFProcessor:
    CHUNK_WORD_TARGET = 2500
    CHUNK_WORD_MAX = 3000
    CHUNK_MAX_BYTES = 512 * 1024  # 512KB

    def __init__(self, file_path: str) -> None:
        self._doc = fitz.open(file_path)
        self._detected_images = False

    @property
    def page_count(self) -> int:
        return len(self._doc)

    @property
    def has_images(self) -> bool:
        return self._detected_images

    def extract_chunks(self) -> Iterator[RawChunk]:
        acc = _ChunkAccumulator()

        for page_idx in range(len(self._doc)):
            page = self._doc[page_idx]
            page_num = page_idx + 1  # 1-based

            images = page.get_images()
            if images:
                self._detected_images = True

            blocks = page.get_text("blocks")

            for block in blocks:
                # block format: (x0, y0, x1, y1, text_or_image, block_no, block_type)
                # block_type: 0=text, 1=image
                block_type = block[6]

                if block_type == 1:
                    # Image block — add image token
                    token = make_image_token(f"page_{page_num}_img", page_num)
                    acc.add_tokens([token], page_num)
                    continue

                text = block[4]
                if not text or not text.strip():
                    continue

                paragraphs = text.strip().split("\n")
                for para_idx, paragraph in enumerate(paragraphs):
                    paragraph = paragraph.strip()
                    if not paragraph:
                        continue

                    is_last_para = para_idx == len(paragraphs) - 1
                    tokens = tokenize_text(
                        paragraph, is_paragraph_end=not is_last_para or True
                    )
                    acc.add_tokens(tokens, page_num)

            if (
                acc.word_count >= self.CHUNK_WORD_TARGET
                or acc.serialized_size >= self.CHUNK_MAX_BYTES
            ):
                yield acc.to_chunk()
                acc.reset()

        if acc.word_count > 0:
            yield acc.to_chunk()

    def close(self) -> None:
        self._doc.close()

    def __enter__(self) -> PDFProcessor:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
