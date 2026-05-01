"""
Unit tests for src/core/api_client/exceptions.py module.
"""

from newapi.api_client.exceptions import (
    CookieError,
    CSRFError,
    LoginError,
    MaxlagError,
    MaxRetriesExceeded,
    WikiClientError,
)


class TestExceptionHierarchy:
    def test_wiki_client_error_is_exception(self):
        assert issubclass(WikiClientError, Exception)

    def test_login_error_is_wiki_client_error(self):
        assert issubclass(LoginError, WikiClientError)

    def test_csrf_error_is_wiki_client_error(self):
        assert issubclass(CSRFError, WikiClientError)

    def test_maxlag_error_is_wiki_client_error(self):
        assert issubclass(MaxlagError, WikiClientError)

    def test_max_retries_exceeded_is_wiki_client_error(self):
        assert issubclass(MaxRetriesExceeded, WikiClientError)

    def test_cookie_error_is_wiki_client_error(self):
        assert issubclass(CookieError, WikiClientError)


class TestExceptionMessages:
    def test_wiki_client_error_message(self):
        err = WikiClientError("test error")
        assert str(err) == "test error"

    def test_login_error_message(self):
        err = LoginError("login failed")
        assert str(err) == "login failed"

    def test_csrf_error_message(self):
        err = CSRFError("bad token")
        assert str(err) == "bad token"
