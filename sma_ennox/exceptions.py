"""Custom exception classes for SMA Ennox library."""


class SMAError(Exception):
    """Base exception for all SMA API errors."""
    pass


class SMAAuthenticationError(SMAError):
    """Raised when authentication fails (login or token refresh)."""
    pass


class SMAAPIError(SMAError):
    """Raised when API request fails."""

    def __init__(self, message: str, status_code: int, response_body: str = ""):
        """
        Initialize API error.

        Args:
            message: Error message
            status_code: HTTP status code
            response_body: Optional response body text
        """
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class SMAConfigError(SMAError):
    """Raised when configuration is invalid or missing."""
    pass


class SMANetworkError(SMAError):
    """Raised when network request fails."""
    pass
