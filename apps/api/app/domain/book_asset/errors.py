class BookAssetError(Exception):
    """Base exception for book asset domain errors."""


class InvalidBookAssetStateError(BookAssetError):
    """Raised when a book asset state transition is invalid."""
