"""
Unit tests for src/core/api_client/client.py module.
"""

from unittest.mock import MagicMock, PropertyMock, patch

import mwclient.errors
import pytest

from newapi.api_client.client import WikiLoginClient
from newapi.api_client.exceptions import LoginError, WikiClientError

# ── Helper to construct a patched WikiLoginClient ────────────────────────────


def _make_client(
    lang: str = "en", family: str = "wikipedia", username: str = "MyBot", password: str = "pass", cookies_dir=None
):
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

        kw = dict(lang=lang, family=family, username=username, password=password)
        if cookies_dir is not None:
            kw["cookies_dir"] = cookies_dir
        client = WikiLoginClient(**kw)
        return client, site_instance


# ── Test _enrich_params ──────────────────────────────────────────────────────


class TestEnrichParams:

    @patch("newapi.api_client.client.mwclient.Site")
    @patch("newapi.api_client.client.get_cookie_path")
    def test_query_action_strips_bot_and_summary(self, mock_path, mock_site) -> None:
        mock_path.return_value = MagicMock()
        mock_site.return_value.api.return_value = {"query": {"userinfo": {"id": 1}}}

        client = WikiLoginClient("en", "wikipedia", "bot", "pass")
        params = {"action": "query", "bot": 1, "summary": "test", "titles": "Python"}
        result = client._enrich_params(params)
        assert "bot" not in result
        assert "summary" not in result
        assert result["titles"] == "Python"

    @patch("newapi.api_client.client.mwclient.Site")
    @patch("newapi.api_client.client.get_cookie_path")
    def test_write_action_injects_bot_and_assertuser(self, mock_path, mock_site) -> None:
        mock_path.return_value = MagicMock()
        mock_site.return_value.api.return_value = {"query": {"userinfo": {"id": 1}}}

        client = WikiLoginClient("en", "wikipedia", "MyBot", "pass")
        params = {"action": "edit", "title": "Test"}
        result = client._enrich_params(params)
        assert result["bot"] == 1
        assert result["assertuser"] == "MyBot"

    def test_wb_action_injects_bot_and_assertuser(self) -> None:
        client, _ = _make_client()
        params = {"action": "wbeditentity", "id": "Q123"}
        result = client._enrich_params(params)
        assert result["bot"] == 1
        assert result["assertuser"] == "MyBot"

    def test_wb_prefix_action_injects_params(self) -> None:
        client, _ = _make_client()
        params = {"action": "wbsetclaim", "claim": "{}"}
        result = client._enrich_params(params)
        assert result["bot"] == 1
        assert result["assertuser"] == "MyBot"

    def test_wikidata_family_injects_params(self) -> None:
        client, _ = _make_client(family="wikidata")
        params = {"action": "parse", "text": "hello"}
        result = client._enrich_params(params)
        assert result["bot"] == 1
        assert result["assertuser"] == "MyBot"

    def test_non_write_action_no_injection(self) -> None:
        client, _ = _make_client()
        params = {"action": "parse", "text": "hello"}
        result = client._enrich_params(params)
        assert "bot" not in result
        assert "assertuser" not in result

    def test_no_action_key_no_injection(self) -> None:
        client, _ = _make_client()
        params = {"titles": "Python"}
        result = client._enrich_params(params)
        assert "bot" not in result
        assert "assertuser" not in result

    def test_does_not_override_existing_bot(self) -> None:
        client, _ = _make_client()
        params = {"action": "edit", "bot": 0}
        result = client._enrich_params(params)
        assert result["bot"] == 0

    def test_empty_username_no_injection(self) -> None:
        client, _ = _make_client(username="")
        params = {"action": "edit", "title": "Test"}
        result = client._enrich_params(params)
        assert "bot" not in result
        assert "assertuser" not in result


# ── Test client_request_retry ──────────────────────────────────────────────────────


class TestClientRequestRetry:
    def test_invalid_method_raises(self) -> None:
        with (
            patch("newapi.api_client.client.mwclient.Site") as mock_site,
            patch("newapi.api_client.client.get_cookie_path"),
        ):
            mock_site.return_value.api.return_value = {"query": {"userinfo": {"id": 1}}}
            client = WikiLoginClient("en", "wikipedia", "bot", "pass")
            with pytest.raises(ValueError, match="method must be"):
                client.client_request_retry({"action": "query"}, method="delete")

    def test_api_error_raises_wiki_client_error(self) -> None:
        with (
            patch("newapi.api_client.client.mwclient.Site") as mock_site,
            patch("newapi.api_client.client.get_cookie_path"),
        ):
            site_instance = mock_site.return_value
            site_instance.api.return_value = {"query": {"userinfo": {"id": 1}}}
            site_instance.connection = MagicMock()
            site_instance.api_url = "http://example.com/api"
            site_instance.get_token = MagicMock(return_value="test_token")

            response = MagicMock()
            response.raise_for_status = MagicMock()
            response.json.return_value = {"error": {"code": "badtoken", "info": "Invalid token"}}
            response.headers = {"Content-Type": "application/json"}
            site_instance.connection.request.return_value = response

            client = WikiLoginClient("en", "wikipedia", "bot", "pass")
            with pytest.raises(WikiClientError):
                client.client_request_retry({"action": "edit"})

    def test_get_request(self) -> None:
        client, site = _make_client()
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json.return_value = {"query": {"pages": {"1": {"title": "Python"}}}}
        response.headers = {"Content-Type": "application/json"}
        site.connection.request.return_value = response

        result = client.client_request_retry({"action": "query", "titles": "Python"}, method="get")
        assert "query" in result
        site.connection.request.assert_called_once()

    def test_post_request(self) -> None:
        client, site = _make_client()
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json.return_value = {"edit": {"result": "Success"}}
        response.headers = {"Content-Type": "application/json"}
        site.connection.request.return_value = response

        result = client.client_request_retry({"action": "edit", "title": "Test"}, method="post")
        assert "edit" in result

    def test_files_forces_post(self) -> None:
        client, site = _make_client()
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json.return_value = {"upload": {"result": "Success"}}
        response.headers = {"Content-Type": "application/json"}
        site.connection.request.return_value = response

        mock_file = MagicMock()
        result = client.client_request_retry(
            {"action": "upload", "filename": "test.png"},
            method="get",
            files={"file": mock_file},
        )
        assert "upload" in result

    def test_success_response_no_error(self) -> None:
        client, site = _make_client()
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json.return_value = {"query": {"userinfo": {"id": 42}}}
        response.headers = {"Content-Type": "application/json"}
        site.connection.request.return_value = response

        result = client.client_request_retry({"action": "query", "meta": "userinfo"})
        assert result["query"]["userinfo"]["id"] == 42


# ── Test _ensure_logged_in ───────────────────────────────────────────────────


class TestEnsureLoggedIn:
    def test_skips_login_when_session_valid(self) -> None:
        client, site = _make_client()
        # uid != 0 means session is valid
        site.api.return_value = {"query": {"userinfo": {"id": 42}}}
        site.login = MagicMock()
        client._ensure_logged_in()
        site.login.assert_not_called()

    def test_logs_in_when_anonymous(self) -> None:
        client, site = _make_client()
        site.logged_in = False
        site.site_init = MagicMock()
        site.login = MagicMock()
        client._ensure_logged_in()
        site.site_init.assert_called_once()

    def test_logs_in_on_api_exception(self) -> None:
        client, site = _make_client()
        site.logged_in = False
        site.site_init = MagicMock(side_effect=Exception("connection error"))
        site.login = MagicMock()
        client._ensure_logged_in()
        site.site_init.assert_called_once()


# ── Test _do_login ───────────────────────────────────────────────────────────


class TestDoLogin:
    def test_login_success(self) -> None:
        client, site = _make_client()
        site.login = MagicMock()
        client._do_login()
        site.login.assert_called_with("MyBot", "pass")
        # mock_save.assert_called_once()

    def test_login_failure_raises_login_error(self) -> None:
        client, site = _make_client()
        site.login = MagicMock(side_effect=mwclient.errors.LoginError(code="bad credentials", info="", site=""))
        with pytest.raises(LoginError, match="login failed"):
            client._do_login()


# ── Test login() public method ───────────────────────────────────────────────


class TestLoginPublic:
    def test_login_calls_do_login(self) -> None:
        client, site = _make_client()
        site.logged_in = False
        with patch.object(client, "_do_login") as mock_do:
            client.login()
            mock_do.assert_called_once()


# ── Test site property ───────────────────────────────────────────────────────


class TestSiteProperty:
    def test_site_returns_mwclient_site(self) -> None:
        client, site = _make_client()
        assert client.site is site


# ── Test __repr__ ────────────────────────────────────────────────────────────


class TestRepr:

    @patch("newapi.api_client.client.mwclient.Site")
    @patch("newapi.api_client.client.get_cookie_path")
    def test_repr(self, mock_path, mock_site) -> None:
        mock_site.return_value.api.return_value = {"query": {"userinfo": {"id": 1}}}
        client = WikiLoginClient("en", "wikipedia", "MyBot", "pass")
        assert "WikiLoginClient" in repr(client)
        assert "en" in repr(client)
        assert "MyBot" in repr(client)

    def test_repr_contains_family(self) -> None:
        client, _ = _make_client(family="wiktionary")
        r = repr(client)
        assert "wiktionary" in r


# ── Test __init__ with cookies_dir ───────────────────────────────────────────


class TestInitCookiesDir:
    def test_passes_cookies_dir_to_get_cookie_path(self) -> None:
        with (
            patch("newapi.api_client.client.mwclient.Site") as mock_site,
            patch("newapi.api_client.client.get_cookie_path") as mock_path,
        ):
            mock_site.return_value.api.return_value = {"query": {"userinfo": {"id": 1}}}
            mock_path.return_value = MagicMock()

            WikiLoginClient("en", "wikipedia", "bot", "pass", cookies_dir="/tmp/cookies")
            mock_path.assert_called_once_with("/tmp/cookies", "wikipedia", "en", "bot")

    def test_default_cookies_dir_is_default_value(self) -> None:
        with (
            patch("newapi.api_client.client.mwclient.Site") as mock_site,
            patch("newapi.api_client.client.get_cookie_path") as mock_path,
        ):
            mock_site.return_value.api.return_value = {"query": {"userinfo": {"id": 1}}}
            mock_path.return_value = MagicMock()

            WikiLoginClient("en", "wikipedia", "bot", "pass", "/tmp/cookies")
            args = mock_path.call_args[0]
            assert args[0] == "/tmp/cookies"
