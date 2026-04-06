class AuthError(Exception):
    """Base exception for auth domain errors."""


class InvalidCredentialsError(AuthError):
    """Raised when login credentials are invalid."""


class EmailAlreadyExistsError(AuthError):
    """Raised when a user with this email already exists."""


class SessionExpiredError(AuthError):
    """Raised when a session has expired."""


class InvalidRefreshTokenError(AuthError):
    """Raised when a refresh token is invalid or not found."""


class InactiveUserError(AuthError):
    """Raised when an inactive user attempts to authenticate."""


class OAuthError(AuthError):
    """Raised when an OAuth flow fails."""
