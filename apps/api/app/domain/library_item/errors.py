class LibraryItemError(Exception):
    """Base exception for library item domain errors."""


class InvalidLibraryItemStateError(LibraryItemError):
    """Raised when an access-status transition or operation is invalid."""
