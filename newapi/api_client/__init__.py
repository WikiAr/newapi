# api_client/__init__.py
# Public surface of the package.
# Import WikiLoginClient and all exception types from here.

from .client import WikiLoginClient
from .exceptions import (
    CookieError,
    CSRFError,
    LoginError,
    MaxlagError,
    MaxRetriesExceeded,
    WikiClientError,
)

__all__ = [
    "WikiLoginClient",
    # Exceptions
    "WikiClientError",
    "LoginError",
    "CSRFError",
    "MaxlagError",
    "MaxRetriesExceeded",
    "CookieError",
]
