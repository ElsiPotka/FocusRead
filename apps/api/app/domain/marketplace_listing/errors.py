class MarketplaceListingError(Exception):
    """Base exception for marketplace listing domain errors."""


class InvalidListingStateError(MarketplaceListingError):
    """Raised when a lifecycle or moderation transition is invalid."""
