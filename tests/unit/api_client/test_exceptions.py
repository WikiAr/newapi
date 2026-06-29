"""
Unit tests for src/core/api_client/exceptions.py module.
"""

from newapi.api_client.exceptions import (
    CookieError,
    CSRFError,
    LoginError,
    MaxlagError,
    MaxRetriesExceededError,
    WikiClientError,
)


class TestExceptionHierarchy:
    def test_wiki_client_error_is_exception(self) -> None:
        assert issubclass(WikiClientError, Exception)

    def test_login_error_is_wiki_client_error(self) -> None:
        assert issubclass(LoginError, WikiClientError)

    def test_csrf_error_is_wiki_client_error(self) -> None:
        assert issubclass(CSRFError, WikiClientError)

    def test_maxlag_error_is_wiki_client_error(self) -> None:
        assert issubclass(MaxlagError, WikiClientError)

    def test_max_retries_exceeded_is_wiki_client_error(self) -> None:
        assert issubclass(MaxRetriesExceededError, WikiClientError)

    def test_cookie_error_is_wiki_client_error(self) -> None:
        assert issubclass(CookieError, WikiClientError)


class TestExceptionMessages:
    def test_wiki_client_error_message(self) -> None:
        err = WikiClientError("test error")
        assert str(err) == "test error"

    def test_login_error_message(self) -> None:
        err = LoginError("login failed")
        assert str(err) == "login failed"

    def test_csrf_error_message(self) -> None:
        err = CSRFError("bad token")
        assert str(err) == "bad token"
