class BookError(Exception):
    """Base exception for book domain errors."""


class InvalidBookStateError(BookError):
    """Raised when a book transition is invalid."""
