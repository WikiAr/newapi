# api_client/exceptions.py
# Typed exceptions so callers can catch specific failure modes.


class WikiClientError(Exception):
    """Base exception for all api_client errors."""


class LoginError(WikiClientError):
    """Raised when credentials are rejected or the login flow fails."""


class CSRFError(WikiClientError):
    """Raised when a CSRF token remains invalid after MAX_RETRIES re-fetches."""


class MaxlagError(WikiClientError):
    """Raised when server maxlag is not resolved after MAX_RETRIES attempts."""


class MaxRetriesExceeded(WikiClientError):
    """Raised when the generic retry cap is hit."""


class CookieError(WikiClientError):
    """Raised when the cookie file cannot be read or written."""
