"""
Refactored API client.

Hierarchy
---------
  RequestsHandler          — transport layer: session, retry loop, CSRF/maxlag/backoff
      └── WikiLoginClient  — business layer: auth, cookie persistence, param enrichment

Examples::

    client = WikiLoginClient(
        lang="en",
        family="wikipedia",
        username="MyBot",
        password="s3cr3t",
    )
    # Simple read
    data = client.client_request({"action": "query", "titles": "Python"})

    # Write — POST with auto CSRF + retry
    data = client.client_request(
        {
            "action": "edit",
            "title": "Sandbox",
            "text": "hello",
            "summary": "test",
        },
        method="post",
    )
"""

from __future__ import annotations

import copy
import logging
from typing import Any, Callable, Union

import mwclient
import mwclient.errors

from .cookies_client import CookiesClient
from .exceptions import LoginError, WikiClientError
from .requests_handler import RequestsHandler

logger = logging.getLogger(__name__)

skip_log_params = [
    "token",
    "password",
    "lgpassword",
    "text",
]

# ---------------------------------------------------------------------------
# WikiLoginClient — business layer
# ---------------------------------------------------------------------------


class WikiLoginClient:
    """
    A thin wrapper around ``mwclient.Site`` that:

    - Persists the session across script runs via a Mozilla cookie jar.
    - Skips the login round-trip when saved cookies are still valid.
    - Transparently retries requests on CSRF errors and server maxlag.
    - Recovers if the session expires mid-run (``assertnameduserfailed``).
    - Injects ``bot=1`` and ``assertuser`` into all write-action requests.

    ``RequestsHandler`` provides the transport/retry layer; this class owns
    only auth logic, parameter enrichment, and continuation pagination.

    Usage::

        client = WikiLoginClient(lang="en", family="wikipedia", username="MyBot", password="s3cr3t")
        data = client.client_request({"action": "query", "titles": "Python"})
    """

    # Write actions that need bot=1 and assertuser injected
    _WRITE_ACTIONS: frozenset[str] = frozenset(
        {
            "edit",
            "create",
            "upload",
            "delete",
            "move",
            "wbeditentity",
            "wbsetclaim",
            "wbcreateclaim",
            "wbsetreference",
            "wbremovereferences",
            "wbsetaliases",
            "wbsetdescription",
            "wbsetlabel",
            "wbsetsitelink",
            "wbmergeitems",
            "wbcreateredirect",
        }
    )

    def __init__(
        self,
        lang: str,
        family: str,
        username: str,
        password: str,
        cookies_dir: str | None = None,
        use_cookies: None | bool = None,
        max_retries: int = 5,
        backoff_base: int = 1,
        maxlag_header: str = "Retry-After",
    ) -> None:
        """
        Initialise the client, load any saved cookies, and ensure the session
        is authenticated before returning.

        Args:
            lang:        Language code, e.g. "en", "de", "ar".
            family:      Site family, e.g. "wikipedia", "wiktionary", "wikidata".
            username:    Bot / user account name (bot-password suffix supported,
                         e.g. "MyBot@BotPassword").
            password:    Account password or bot password.
            cookies_dir: Directory where cookie files are stored.
        """
        self.lang = lang
        self.family = family
        self.username = username
        self._password = password  # kept private — never log or expose this

        self.cookies_client = CookiesClient(lang, family, username, cookies_dir, use_cookies)

        # ── mwclient Site ──────────────────────────────────────────────────
        logger.debug("Creating mwclient.Site for %s.%s.org", lang, family)
        self.api_url = self._make_api_url()

        try:
            self._site = mwclient.Site(f"{self.lang}.{self.family}.org", do_init=False)
        except Exception as exc:
            raise WikiClientError(f"Invalid site ID: {self.lang}.{self.family}.org") from exc

        # ── Inject saved cookies ───────────────────────────────────────────
        # mwclient stores its requests.Session at site.connection.

        self.cookies_client.set_site_cookies(self._site)

        # ── Wrap the session with retry / CSRF / maxlag logic ──────────────
        # wrap_session(self._site.connection, self._site)

        # ── Authenticate if necessary ──────────────────────────────────────
        self._ensure_logged_in()

        self.requests_handler = RequestsHandler(
            max_retries=max_retries,
            backoff_base=backoff_base,
            maxlag_header=maxlag_header,
            _site=self._site,
            on_assertnameduserfailed=self._on_assertnameduserfailed,
        )

    def _make_api_url(self) -> str:
        api_url = f"https://{self.lang}.{self.family}.org/w/api.php"

        if api_url == "https://www.mdwiki.org/w/api.php":
            api_url = "https://mdwiki.org/w/api.php"
        return api_url

    # ------------------------------------------------------------------
    # RequestsHandler contract — concrete implementations
    # ------------------------------------------------------------------

    def _on_assertnameduserfailed(self) -> None:
        """
        Session expired mid-run: nuke stale cookies and re-authenticate.
        Called by the base-class retry loop; never call directly.
        """
        logger.warning(
            "assertnameduserfailed for %s on %s.%s.org — clearing cookies and re-logging in",
            self.username,
            self.lang,
            self.family,
        )
        self.cookies_client.delete_cookie_file(reason="assertnameduserfailed")
        self._do_login()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def site(self) -> mwclient.Site:
        """The underlying ``mwclient.Site`` — use for high-level wiki access."""
        return self._site

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _client_request(
        self,
        params: dict,
        method: str = "post",
        files: Any | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Send a GET or POST request to the wiki API and return parsed JSON.

        CSRF tokens, maxlag backoff, and ``assertnameduserfailed`` recovery are
        all handled transparently by the ``RequestsHandler`` base class.

        Args:
            params: MediaWiki API parameters. ``format`` defaults to ``"json"``.
            method: ``"get"`` or ``"post"`` (case-insensitive).
                    Files automatically force POST.
            files:  ``{field_name: file-like}`` for multipart uploads.

        Returns:
            Parsed JSON response dict.

        Raises:
            ValueError:         On invalid *method*.
            CSRFError:          CSRF token invalid after all retries.
            MaxlagError:        Server maxlag unresolved after all retries.
            WikiClientError:    On other API-level errors.
            requests.HTTPError: On non-2xx HTTP responses.
        """
        method = method.lower()
        if method not in ("get", "post"):
            raise ValueError(f"method must be 'get' or 'post', got {method!r}")

        method = method.upper()

        # Files can only travel via multipart POST
        action = params.get("action")
        if action in self._WRITE_ACTIONS or files is not None:
            method = "POST"

        # Always request JSON and inject write-action safety params
        params = self._enrich_params({"format": "json", **params})

        logger.debug(
            "%s %s params=%s files=%s",
            method.upper(),
            self.api_url,
            # Never log token values
            {k: ("***" if k in skip_log_params else v) for k, v in params.items()},
            list(files.keys()) if files else None,
        )

        # Fetch a CSRF token now if the caller didn't supply one.
        # The retry loop will refresh it automatically on CSRF errors.
        if method == "POST" and "token" not in params:
            params["token"] = self._site.get_token("csrf")

        args = {}

        if method == "GET":
            args["params"] = params
        else:
            args["data"] = params
            if files:
                args["files"] = files

        return self.requests_handler._request_with_retry(
            method,
            self.api_url,
            **args,
        )

    def _ensure_logged_in(self) -> None:
        """
        Check whether the current session is authenticated.
        """
        # if self._site.logged_in:
        if getattr(self._site, "logged_in", None):
            logger.info(f"Session already authenticated {self._site.logged_in=}")
            return

        if not self.cookies_client.is_cookie_path_exists():
            return

        try:
            self._site.site_init()
            if self._site.logged_in:
                logger.info("Revived session via cookies as %s", self._site.username)
                return
        except Exception:
            logger.exception("Error in site_init")

        # if not self._site.logged_in: self._do_login()
        # don't login yet, user can use login() method

    def _enrich_params(self, params: dict) -> dict[str, Any]:
        """
        Inject write-action safety parameters.

        For write actions:
          - ``bot=1``        marks edits as bot edits in recent changes.
          - ``assertuser``   ensures the API rejects requests from the wrong
                             account (guards against accidental edits).

        Query actions have write-only keys scrubbed instead.
        """
        params = dict(params)
        action = params.get("action", "")

        # Strip write-only params from query actions
        if action == "query":
            params.pop("bot", None)
            params.pop("summary", None)
            return params

        # Inject bot marker and identity assertion for all write actions
        is_write = action in self._WRITE_ACTIONS or action.startswith("wb") or self.family == "wikidata"
        if is_write and self.username:
            params.setdefault("bot", 1)
            params.setdefault("assertuser", self.username)

        return params

    def _do_login(self) -> None:
        """
        Execute the mwclient login handshake and persist the resulting cookies.

        Raises:
            LoginError: if mwclient rejects the credentials.
        """
        try:
            self._site.login(self.username, self._password)
        except mwclient.errors.LoginError as exc:
            raise LoginError(f"login failed for {self.username} on {self.lang}.{self.family}.org: {exc}") from exc

        if self._site.logged_in:
            logger.info(
                "Logged in successfully as %s on %s.%s.org",
                self.username,
                self.lang,
                self.family,
            )
            self.cookies_client.save_cookies_cj()

    # ── Public methods ─────────────────────────────────────────────────────

    def login(self, force: bool = False) -> None:
        """
        Force a fresh login regardless of cookie state.

        Call this if you know the session has expired and want to re-authenticate
        without creating a new WikiLoginClient instance.
        """
        if force or not self._site.logged_in:
            logger.info(
                "Forcing re-login for %s on %s.%s.org",
                self.username,
                self.lang,
                self.family,
            )
            self._do_login()

    def client_request(
        self,
        params: dict,
        method: str = "post",
        files: Any | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """ """
        return self._client_request(
            params=params,
            method=method,
            files=files,
            **kwargs,
        )

    def client_request_safe(
        self,
        params: dict,
        method: str = "post",
        files: Any | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """ """
        try:
            return self._client_request(
                params=params,
                method=method,
                files=files,
                **kwargs,
            )
        except Exception as exc:
            logger.warning("client_request_safe: %s", exc)
            return {}

    def client_request_retry(
        self,
        params: dict,
        method: str = "post",
        files: Any | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """ """
        method = method.lower()
        if method not in ("get", "post"):
            raise ValueError(f"method must be 'get' or 'post', got {method!r}")

        return self._client_request(
            params=params,
            method=method,
            files=files,
            **kwargs,
        )

    def post_continue(
        self,
        params: dict,
        action: str,
        _p_: str | None = None,
        p_empty: Union[list, dict] | None = None,
        max: int | None = None,
        first: int | None = None,
        _p_2: str | None = None,
        _p_2_empty: Union[list, dict] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Drive a MediaWiki API continuation query to completion.

        Iterates the ``continue`` token until all pages are fetched or *max*
        results have been collected.

        Args:
            params:     Base API parameters.
            action:     Top-level JSON key to extract results from
                        (e.g. ``"query"``).
            _p_:        Sub-key inside *action* (default ``"pages"``).
            p_empty:    Seed value for the accumulator (list or dict).
            max:        Stop accumulating after this many results.
            first:      Return only the first element of the result list.
            _p_2:       Secondary sub-key when *first* is True.
            _p_2_empty: Seed for secondary accumulator.

        Returns:
            Accumulated results as a list or dict, depending on *p_empty*.
        """
        logger.debug("action=%s _p_=%s", action, _p_)

        if isinstance(max, str) and max.isdigit():
            max = int(max)
        if max == 0:
            max = 500_000

        p_empty = p_empty if p_empty is not None else []
        _p_2_empty = _p_2_empty if _p_2_empty is not None else []

        results = p_empty
        continue_params: dict = {}
        iterations = 0

        while continue_params or iterations == 0:
            page_params = copy.deepcopy(params)
            iterations += 1

            if continue_params:
                logger.debug("Applying continue_params: %s", continue_params)
                page_params.update(continue_params)

            body = self.client_request_safe(page_params)

            if not body:
                logger.debug("empty response, stopping")
                break

            continue_params = {}

            if action == "wbsearchentities":
                data = body.get("search", [])
            else:
                continue_params = body.get("continue", {})
                data = body.get(action, {}).get(_p_, p_empty)

                if _p_ == "querypage":
                    data = data.get("results", [])
                elif first:
                    if isinstance(data, list) and data:
                        data = data[0]
                        if _p_2:
                            data = data.get(_p_2, _p_2_empty)

            if not data:
                logger.debug("no data in response, stopping")
                break

            logger.debug("+%d items (total %d)", len(data), len(results))

            if len(results) >= max:
                logger.debug("max=%d reached, stopping", max)
                break

            if isinstance(results, list):
                results.extend(data)
            else:
                results = {**results, **data}

        logger.debug("done, %d total results", len(results))
        return results

    def post_continue_list(
        self,
        params: dict,
        action: str,
        _load_data: Callable,
        max: int | None = None,
    ) -> list[Any]:
        """
        Drive a MediaWiki API continuation query to completion.

        Iterates the ``continue`` token until all pages are fetched or *max*
        results have been collected.

        Args:
            params:     Base API parameters.
            action:     Top-level JSON key to extract results from
                        (e.g. ``"query"``).
            max:        Stop accumulating after this many results.

        Returns:
            Accumulated results as a list
        """
        logger.debug("action=%s", action)

        if isinstance(max, str) and max.isdigit():
            max = int(max)
        if max == 0:
            max = 500_000
        if max is None:
            max = 500_000
        results = []
        continue_params: dict = {}
        iterations = 0

        while continue_params or iterations == 0:
            page_params = copy.deepcopy(params)
            iterations += 1

            if continue_params:
                logger.debug("Applying continue_params: %s", continue_params)
                page_params.update(continue_params)

            body = self.client_request_safe(page_params)

            if not body:
                logger.debug("empty response, stopping")
                break

            continue_params = body.get("continue", {})

            data = _load_data(body)

            if not data:
                logger.debug("no data in response, stopping")
                break

            logger.debug("+%d items (total %d)", len(data), len(results))

            if len(results) >= max:
                logger.debug("max=%d reached, stopping", max)
                break

            results.extend(data)

        logger.debug("done, %d total results", len(results))
        return results

    def __repr__(self) -> str:
        return f"WikiLoginClient(lang={self.lang!r}, family={self.family!r}, username={self.username!r})"


__all__ = [
    "WikiLoginClient",
]
