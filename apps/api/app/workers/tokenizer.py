"""
Pure-function tokenizer for converting extracted text into compact word tokens.

Token format (compact array for persistence/cache/API):
  ["w", "word_text", pause_multiplier]   — word token
  ["i", "image_path", page_number]       — image token

Pause multipliers:
  1.0 — default (no trailing punctuation)
  1.3 — comma, semicolon, colon
  2.0 — period, exclamation, question mark
  2.5 — paragraph break (last word of a paragraph)
  0.0 — image token (not a timed word)
"""

from __future__ import annotations

PAUSE_DEFAULT: float = 1.0
PAUSE_COMMA: float = 1.3
PAUSE_SENTENCE: float = 2.0
PAUSE_PARAGRAPH: float = 2.5


def compute_pause(word: str, *, is_paragraph_end: bool = False) -> float:
    if not word:
        return PAUSE_DEFAULT

    last_char = word[-1]

    if is_paragraph_end:
        return PAUSE_PARAGRAPH

    if last_char in ".!?":
        return PAUSE_SENTENCE

    if last_char in ",;:":
        return PAUSE_COMMA

    return PAUSE_DEFAULT


def tokenize_text(text: str, *, is_paragraph_end: bool = False) -> list[list]:
    words = text.split()
    if not words:
        return []

    tokens: list[list] = []
    for i, word in enumerate(words):
        is_last = i == len(words) - 1
        pause = compute_pause(word, is_paragraph_end=is_last and is_paragraph_end)
        tokens.append(["w", word, pause])

    return tokens


def make_image_token(image_path: str, page_number: int) -> list:
    return ["i", image_path, page_number]
