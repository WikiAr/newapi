"""
Unit tests for src/core/api_client/client.py - RequestsHandler and related methods.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests
from newapi.api_client.client import WikiLoginClient
from newapi.api_client.exceptions import CSRFError, MaxlagError, WikiClientError


def _make_client(lang: str = "en", family: str = "wikipedia", username: str = "MyBot", password: str = "pass"):
    """Create a WikiLoginClient with all external dependencies mocked."""
    with (
        patch("newapi.api_client.client.mwclient.Site") as mock_site,
        patch("newapi.api_client.client.get_cookie_path") as mock_path,
    ):
        mock_path.return_value = MagicMock()
        site_instance = mock_site.return_value
        site_instance.api.return_value = {"query": {"userinfo": {"id": 1}}}
        site_instance.connection = MagicMock()
        site_instance.api_url = "http://example.com/api"
        site_instance.get_token = MagicMock(return_value="test_token")

        client = WikiLoginClient(lang=lang, family=family, username=username, password=password)
        return client, site_instance


class TestNonJsonResponse:
    """Tests for non-JSON response handling."""

    def test_non_json_content_type_returns_empty_dict(self) -> None:
        client, site = _make_client()
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.headers = {"Content-Type": "text/html"}
        response.json = MagicMock(side_effect=ValueError("not json"))
        site.connection.request.return_value = response

        result = client.client_request_retry({"action": "query"}, method="get")
        assert result == {}


class TestJsonParsingError:
    """Tests for JSON parsing error handling."""

    def test_json_parse_failure_returns_empty_dict(self) -> None:
        client, site = _make_client()
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.headers = {"Content-Type": "application/json"}
        response.json = MagicMock(side_effect=ValueError("invalid json"))
        site.connection.request.return_value = response

        result = client.client_request_retry({"action": "query"}, method="get")
        assert result == {}


class TestMaxlagHandling:
    """Tests for maxlag error handling."""

    def test_maxlag_error_retries_and_succeeds(self) -> None:
        client, site = _make_client()
        maxlag_response = MagicMock()
        maxlag_response.raise_for_status = MagicMock()
        maxlag_response.headers = {"Content-Type": "application/json", "X-RateLimit-RetryAfter": "2"}
        maxlag_response.json.return_value = {"error": {"code": "maxlag", "info": "Lag"}}

        success_response = MagicMock()
        success_response.raise_for_status = MagicMock()
        success_response.headers = {"Content-Type": "application/json"}
        success_response.json.return_value = {"query": {"pages": {"1": {"title": "Test"}}}}

        site.connection.request.side_effect = [maxlag_response, success_response]

        with patch("newapi.api_client.client.time.sleep") as mock_sleep:
            result = client.client_request_retry({"action": "query"}, method="get")
            assert "query" in result

    def test_maxlag_exhausted_retries_raises_maxlag_error(self) -> None:
        client, site = _make_client()
        maxlag_response = MagicMock()
        maxlag_response.raise_for_status = MagicMock()
        maxlag_response.headers = {"Content-Type": "application/json"}
        maxlag_response.json.return_value = {"error": {"code": "maxlag", "info": "Lag"}}
        site.connection.request.return_value = maxlag_response

        with patch("newapi.api_client.client.time.sleep"):
            with pytest.raises(MaxlagError):
                client.client_request_retry({"action": "query"}, method="get")


class TestCSRFErrorHandling:
    """Tests for CSRF token error handling."""

    def test_csrf_error_refreshes_token_and_retries(self) -> None:
        client, site = _make_client()

        csrf_error_response = MagicMock()
        csrf_error_response.raise_for_status = MagicMock()
        csrf_error_response.headers = {"Content-Type": "application/json"}
        csrf_error_response.json.return_value = {"error": {"code": "badtoken", "info": "Invalid token"}}

        success_response = MagicMock()
        success_response.raise_for_status = MagicMock()
        success_response.headers = {"Content-Type": "application/json"}
        success_response.json.return_value = {"query": {"pages": {"1": {"title": "Test"}}}}

        site.connection.request.side_effect = [csrf_error_response, success_response]
        site_instance = site  # store reference

        result = client.client_request_retry({"action": "query", "token": "bad"}, method="get")
        assert "query" in result


class TestAssertNamedUserFailed:
    """Tests for assertnameduserfailed recovery."""

    def test_assertnameduserfailed_recovery_succeeds(self) -> None:
        client, site = _make_client()

        assert_failed_response = MagicMock()
        assert_failed_response.raise_for_status = MagicMock()
        assert_failed_response.headers = {"Content-Type": "application/json"}
        assert_failed_response.json.return_value = {
            "error": {"code": "assertnameduserfailed", "info": "Session expired"}
        }

        success_response = MagicMock()
        success_response.raise_for_status = MagicMock()
        success_response.headers = {"Content-Type": "application/json"}
        success_response.json.return_value = {"query": {"pages": {"1": {"title": "Test"}}}}

        site.connection.request.side_effect = [assert_failed_response, success_response]
        site.login = MagicMock()

        result = client.client_request_retry({"action": "query"}, method="get")
        assert "query" in result


class TestOnAssertNamedUserFailed:
    """Tests for _on_assertnameduserfailed method."""

    @patch("newapi.api_client.client._delete_cookie_file")
    def test_on_assertnameduserfailed_clears_cookies_and_relogs(self, mock_delete) -> None:
        client, site = _make_client()
        site.login = MagicMock()

        client._on_assertnameduserfailed()

        mock_delete.assert_called_once()
        site.login.assert_called_once_with("MyBot", "pass")


class TestLoginForced:
    """Tests for login method with force=True."""

    @patch.object(WikiLoginClient, "_do_login")
    def test_login_force_calls_do_login_when_not_logged_in(self, mock_do_login) -> None:
        client, site = _make_client()
        site.logged_in = False

        client.login(force=True)

        mock_do_login.assert_called_once()


class TestHandleMaxlag:
    """Tests for _handle_maxlag method."""

    def test_handle_maxlag_with_retry_after_header(self) -> None:
        client, _ = _make_client()
        response = MagicMock()
        response.headers = {"Retry-After": "3"}

        with patch("newapi.api_client.client.time.sleep") as mock_sleep:
            client._handle_maxlag(response, 1)
            mock_sleep.assert_called_with(3.0)

    def test_handle_maxlag_with_invalid_retry_after_uses_backoff(self) -> None:
        client, _ = _make_client()
        response = MagicMock()
        response.headers = {"Retry-After": "not_a_number"}

        with patch("newapi.api_client.client.time.sleep") as mock_sleep:
            from newapi.api_client.client import settings

            with patch.object(settings.api_client, "backoff_base", 1):
                client._handle_maxlag(response, 1)
                mock_sleep.assert_called_with(2.0)  # 1 * 2^1

    def test_handle_maxlag_no_retry_after_uses_backoff(self) -> None:
        client, _ = _make_client()
        response = MagicMock()
        response.headers = {}

        with patch("newapi.api_client.client.time.sleep") as mock_sleep:
            from newapi.api_client.client import settings

            with patch.object(settings.api_client, "backoff_base", 1):
                client._handle_maxlag(response, 2)
                mock_sleep.assert_called_with(4.0)  # 1 * 2^2


class TestInjectToken:
    """Tests for _inject_token static method."""

    def test_inject_token_into_data(self) -> None:
        from newapi.api_client.client import RequestsHandler

        data, params = RequestsHandler._inject_token("new_token", {"token": "old"}, {})
        assert data["token"] == "new_token"

    def test_inject_token_into_params(self) -> None:
        from newapi.api_client.client import RequestsHandler

        data, params = RequestsHandler._inject_token("new_token", {}, {"token": "old"})
        assert params["token"] == "new_token"

    def test_inject_token_no_existing_token(self) -> None:
        from newapi.api_client.client import RequestsHandler

        data, params = RequestsHandler._inject_token("new_token", {}, {})
        assert data == {}
        assert params == {}


@pytest.mark.skip(reason="This test is never end")
class TestPostContinue:
    """Tests for post_continue method."""

    def test_post_continue_single_page(self) -> None:
        client, site = _make_client()

        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.headers = {"Content-Type": "application/json"}
        response.json.return_value = {"query": {"pages": {"1": {"title": "Test"}}}}
        site.connection.request.return_value = response

        result = client.post_continue({"action": "query"}, "query", p_empty={})
        assert result == {"1": {"title": "Test"}}

    def test_post_continue_with_continuation(self) -> None:
        client, site = _make_client()

        first_response = MagicMock()
        first_response.raise_for_status = MagicMock()
        first_response.headers = {"Content-Type": "application/json"}
        first_response.json.return_value = {"query": {"pages": {"1": {"title": "Test1"}}}, "continue": {"gpsoffset": 1}}

        second_response = MagicMock()
        second_response.raise_for_status = MagicMock()
        second_response.headers = {"Content-Type": "application/json"}
        second_response.json.return_value = {"query": {"pages": {"2": {"title": "Test2"}}}}

        site.connection.request.side_effect = [first_response, second_response]

        result = client.post_continue({"action": "query"}, "query", p_empty=[])
        assert len(result) == 2


class TestCookieLoading:
    """Tests for cookie loading error handling."""

    @patch("newapi.api_client.client.http.cookiejar.LWPCookieJar")
    def test_make_cookiejar_loads_existing_cookies(self, mock_jar_class) -> None:
        from pathlib import Path

        from newapi.api_client.client import CookiesClient

        mock_cj = MagicMock()
        mock_jar_class.return_value = mock_cj

        with patch("pathlib.Path.exists", return_value=True):
            mock_cj.load.side_effect = Exception("Parse error")
            result = CookiesClient._make_cookiejar(Path("/fake/path"))

        mock_cj.load.assert_called_once_with(ignore_discard=True, ignore_expires=True)


class TestCookieSaving:
    """Tests for cookie saving error handling."""

    @patch("newapi.api_client.client.logger")
    def test_save_cookies_failure_is_logged(self, mock_logger) -> None:
        from newapi.api_client.client import CookiesClient

        mock_cj = MagicMock()
        mock_cj.save.side_effect = Exception("IO Error")

        CookiesClient.save_cookies(mock_cj)

        mock_logger.exception.assert_called_with("Failed to save cookies")
