"""
Exception hierarchy for mw_api.

Provides typed exceptions for consistent error handling across the codebase,
replacing the inconsistent return types (str, bool, None) in error handling.
"""

from typing import Any, Dict, Optional


class NewApiException(Exception):
    """
    Base exception for all mw_api errors.

    All custom exceptions in the library should inherit from this class.
    """

    def __init__(self, message: str = "", code: str = "") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class ApiError(NewApiException):
    """
    Exception for MediaWiki API errors.

    Represents errors returned by the MediaWiki API.

    Attributes:
        code: The error code from the API (e.g., 'articleexists').
        message: Human-readable error message.
        info: Additional info from the API.
        is_retryable: Whether the operation can be retried.
    """

    def __init__(
        self,
        code: str,
        message: str,
        info: str = "",
        is_retryable: bool = False,
        raw_error: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.info = info
        self.is_retryable = is_retryable
        self.raw_error = raw_error or {}
        super().__init__(f"{code}: {message}", code=code)


class AbuseFilterError(ApiError):
    """
    Exception for abuse filter blocks.

    Raised when an edit is blocked by an abuse filter.

    Attributes:
        filter_id: The ID of the abuse filter that blocked the action.
        description: Description of the filter rule.
    """

    def __init__(
        self,
        description: str,
        filter_id: str = "",
        raw_error: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.filter_id = filter_id
        self.description = description
        super().__init__(
            code="abusefilter-disallowed",
            message=description,
            info=f"Filter ID: {filter_id}",
            is_retryable=False,
            raw_error=raw_error,
        )


class MaxLagError(ApiError):
    """
    Exception for database lag errors.

    Raised when the database replication lag is too high.
    This is a retryable error.

    Attributes:
        lag: The current replication lag in seconds.
    """

    def __init__(
        self,
        lag: int = 0,
        message: str = "Database lag is too high",
        raw_error: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.lag = lag
        super().__init__(
            code="maxlag",
            message=message,
            info=f"Lag: {lag} seconds",
            is_retryable=True,
            raw_error=raw_error,
        )


class ArticleExistsError(ApiError):
    """
    Exception when trying to create an article that already exists.
    """

    def __init__(
        self,
        message: str = "The article you tried to create has been created already.",
        raw_error: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            code="articleexists",
            message=message,
            is_retryable=False,
            raw_error=raw_error,
        )


class NoSuchEntityError(ApiError):
    """
    Exception when a Wikidata entity does not exist.
    """

    def __init__(
        self,
        message: str = "The entity does not exist.",
        raw_error: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            code="no-such-entity",
            message=message,
            is_retryable=False,
            raw_error=raw_error,
        )


class ProtectedPageError(ApiError):
    """
    Exception when trying to edit a protected page.
    """

    def __init__(
        self,
        message: str = "The page is protected.",
        raw_error: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            code="protectedpage",
            message=message,
            is_retryable=False,
            raw_error=raw_error,
        )


class InvalidTokenError(ApiError):
    """
    Exception for invalid CSRF token.

    This is a retryable error - the token should be refreshed.
    """

    def __init__(
        self,
        message: str = "Invalid CSRF token.",
        raw_error: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(code="badtoken", message=message, is_retryable=True, raw_error=raw_error)


class AuthenticationError(NewApiException):
    """
    Exception for authentication failures.
    """

    def __init__(self, message: str = "Authentication failed.") -> None:
        super().__init__(message, code="auth_failed")


class ValidationError(NewApiException):
    """
    Exception for validation errors in input data.
    """

    def __init__(self, message: str, field: str = "") -> None:
        self.field = field
        super().__init__(message, code="validation_error")


def parse_api_error(error_dict: Dict[str, Any]) -> Optional[ApiError]:
    """
    Parse an API error dictionary and return the appropriate exception.

    Args:
        error_dict: The error dictionary from the API response.

    Returns:
        An ApiError subclass instance, or None if the error cannot be parsed.
    """
    if not error_dict:
        return None

    code = error_dict.get("code", "")
    info = error_dict.get("info", "")

    # Map error codes to exception classes
    if code == "abusefilter-disallowed":
        abusefilter = error_dict.get("abusefilter", {})
        description = abusefilter.get("description", "")
        filter_id = str(abusefilter.get("id", ""))
        return AbuseFilterError(description=description, filter_id=filter_id, raw_error=error_dict)

    if code == "maxlag":
        lag = int(error_dict.get("lag", 0))
        return MaxLagError(lag=lag, message=info, raw_error=error_dict)

    if code == "articleexists":
        return ArticleExistsError(message=info, raw_error=error_dict)

    if code == "no-such-entity":
        return NoSuchEntityError(message=info, raw_error=error_dict)

    if code == "protectedpage":
        return ProtectedPageError(message=info, raw_error=error_dict)

    if code == "badtoken" or info == "Invalid CSRF token.":
        return InvalidTokenError(message=info, raw_error=error_dict)

    # Generic API error for unknown codes
    return ApiError(code=code, message=info, is_retryable=False, raw_error=error_dict)
