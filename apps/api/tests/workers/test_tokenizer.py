from __future__ import annotations

from app.workers.tokenizer import (
    PAUSE_COMMA,
    PAUSE_DEFAULT,
    PAUSE_PARAGRAPH,
    PAUSE_SENTENCE,
    compute_pause,
    make_image_token,
    tokenize_text,
)


class TestComputePause:
    def test_default_for_plain_word(self):
        assert compute_pause("hello") == PAUSE_DEFAULT

    def test_comma(self):
        assert compute_pause("however,") == PAUSE_COMMA

    def test_semicolon(self):
        assert compute_pause("done;") == PAUSE_COMMA

    def test_colon(self):
        assert compute_pause("note:") == PAUSE_COMMA

    def test_period(self):
        assert compute_pause("end.") == PAUSE_SENTENCE

    def test_exclamation(self):
        assert compute_pause("wow!") == PAUSE_SENTENCE

    def test_question_mark(self):
        assert compute_pause("really?") == PAUSE_SENTENCE

    def test_paragraph_end_overrides_punctuation(self):
        assert compute_pause("word.", is_paragraph_end=True) == PAUSE_PARAGRAPH

    def test_paragraph_end_on_plain_word(self):
        assert compute_pause("word", is_paragraph_end=True) == PAUSE_PARAGRAPH

    def test_empty_string(self):
        assert compute_pause("") == PAUSE_DEFAULT


class TestTokenizeText:
    def test_single_word(self):
        tokens = tokenize_text("hello")
        assert tokens == [["w", "hello", PAUSE_DEFAULT]]

    def test_sentence_with_punctuation(self):
        tokens = tokenize_text("Hello, world.")
        assert len(tokens) == 2
        assert tokens[0] == ["w", "Hello,", PAUSE_COMMA]
        assert tokens[1] == ["w", "world.", PAUSE_SENTENCE]

    def test_paragraph_end_applies_to_last_word(self):
        tokens = tokenize_text("end here", is_paragraph_end=True)
        assert tokens[0] == ["w", "end", PAUSE_DEFAULT]
        assert tokens[1] == ["w", "here", PAUSE_PARAGRAPH]

    def test_paragraph_end_with_punctuation_on_last_word(self):
        tokens = tokenize_text("end here.", is_paragraph_end=True)
        # Paragraph end overrides sentence pause
        assert tokens[1] == ["w", "here.", PAUSE_PARAGRAPH]

    def test_empty_text(self):
        assert tokenize_text("") == []

    def test_whitespace_only(self):
        assert tokenize_text("   ") == []

    def test_multiple_words_default_pause(self):
        tokens = tokenize_text("the quick brown fox")
        assert len(tokens) == 4
        assert all(t[2] == PAUSE_DEFAULT for t in tokens)


class TestMakeImageToken:
    def test_creates_image_token(self):
        token = make_image_token("/images/fig1.png", 12)
        assert token == ["i", "/images/fig1.png", 12]
