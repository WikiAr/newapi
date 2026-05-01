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
import http.cookiejar
import logging
import time
from pathlib import Path
from typing import Any, Optional, Union

import mwclient
import mwclient.errors
import requests

from . import config
from .cookies import _delete_cookie_file, get_cookie_path
from .exceptions import CSRFError, LoginError, MaxlagError, WikiClientError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# RequestsHandler — transport + retry layer
# ---------------------------------------------------------------------------


class RequestsHandler:
    """
    Owns a ``requests.Session`` and drives every HTTP call through a unified
    retry loop that handles:

    - CSRF / bad token  → refresh token, reinject, retry
    - maxlag            → exponential back-off, retry
    - assertnameduserfailed → delegate re-login hook, retry

    Subclasses must supply ``_session`` (a ``requests.Session``) and may
    override ``_on_assertnameduserfailed`` to implement session recovery.
    """

    # ------------------------------------------------------------------
    # Abstract-ish contract that subclasses must satisfy
    # ------------------------------------------------------------------

    @property
    def _session(self) -> requests.Session:
        """The live ``requests.Session``.  Subclasses must assign this."""
        raise NotImplementedError  # pragma: no cover

    def _refresh_csrf_token(self) -> str:
        """
        Fetch and return a fresh CSRF token.
        Subclasses override this to call ``site.get_token("csrf", force=True)``.
        """
        raise NotImplementedError  # pragma: no cover

    def _on_assertnameduserfailed(self) -> None:
        """
        Called when the API returns ``assertnameduserfailed``.
        Subclasses implement session-recovery logic (re-login, cookie reset).
        """
        raise NotImplementedError  # pragma: no cover

    # ------------------------------------------------------------------
    # Core request execution — the only method that touches the network
    # ------------------------------------------------------------------

    def _execute_request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        files: Optional[Any] = None,
    ) -> requests.Response:
        """
        Send one HTTP request through the session with no retry logic.
        Returns the raw ``requests.Response``.
        """
        return self._session.request(
            method,
            url,
            params=params,
            data=data,
            files=files,
        )

    # ------------------------------------------------------------------
    # Retry loop  (called by WikiLoginClient.client_request)
    # ------------------------------------------------------------------

    def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        files: Optional[Any] = None,
        assertnameduser_retries: int = 1,
    ) -> dict:
        """
        Execute a request and automatically retry on transient API errors.

        Retry conditions (each counted against ``config.MAX_RETRIES``):
          - CSRF / bad token  → ``_handle_csrf``  → inject new token, retry
          - maxlag            → ``_handle_maxlag`` → sleep, retry
          - assertnameduserfailed → ``_on_assertnameduserfailed`` → retry once

        All other errors bubble up unchanged.

        Returns:
            Parsed JSON response dict.

        Raises:
            CSRFError, MaxlagError: after exhausting retries.
            WikiClientError:        on assertnameduserfailed after recovery.
            requests.HTTPError:     on non-2xx HTTP status.
        """
        # Mutable copies so per-retry mutations (token reinject) stay local
        # to this call and don't bleed into the caller's dict.
        working_params = dict(params) if params else {}
        working_data = dict(data) if data else {}

        attempt = 0
        named_user_attempts = 0

        while attempt < config.MAX_RETRIES:
            response = self._execute_request(
                method,
                url,
                params=working_params or None,
                data=working_data or None,
                files=files,
            )
            response.raise_for_status()

            # Non-JSON responses (e.g. uploads returning HTML) go straight back
            content_type = response.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                return {}

            try:
                body: dict = response.json()
            except ValueError:
                return {}

            error = body.get("error", {})
            if not error:
                return body  # ← happy path

            error_code: str = error.get("code", "")
            error_info: str = error.get("info", "")

            # ── CSRF ──────────────────────────────────────────────────────
            if self._is_csrf_error(error_code, error_info):
                attempt += 1
                if attempt >= config.MAX_RETRIES:
                    raise CSRFError(
                        f"CSRF token remained invalid after {config.MAX_RETRIES} "
                        f"attempts. Last error: {error_info or error_code}"
                    )
                working_data, working_params = self._handle_csrf(
                    error_code, error_info, attempt, working_data, working_params
                )
                continue

            # ── maxlag ────────────────────────────────────────────────────
            if error_code == "maxlag":
                attempt += 1
                if attempt >= config.MAX_RETRIES:
                    raise MaxlagError(
                        f"Server maxlag not resolved after {config.MAX_RETRIES} attempts."
                    )
                self._handle_maxlag(response, attempt)
                continue

            # ── assertnameduserfailed ─────────────────────────────────────
            if error_code == "assertnameduserfailed":
                if named_user_attempts >= assertnameduser_retries:
                    raise WikiClientError(
                        "assertnameduserfailed persists after re-login"
                    )
                named_user_attempts += 1
                logger.warning(
                    "assertnameduserfailed — attempting recovery (try %d/%d)",
                    named_user_attempts,
                    assertnameduser_retries,
                )
                self._on_assertnameduserfailed()
                # Reset the retry counter so maxlag/csrf budget is fresh
                attempt = 0
                continue

            # ── any other error — let the caller decide ───────────────────
            raise WikiClientError(f"API error {error_code}: {error_info}")

        raise MaxlagError(
            f"Exceeded {config.MAX_RETRIES} retries without a successful response."
        )

    # ------------------------------------------------------------------
    # Protected CSRF helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_csrf_error(code: str, info: str) -> bool:
        return code in ("badtoken", "notoken") or info == "Invalid CSRF token."

    def _handle_csrf(
        self,
        error_code: str,
        error_info: str,
        attempt: int,
        data: dict,
        params: dict,
    ) -> tuple[dict, dict]:
        """
        Refresh the CSRF token and reinject it into whichever dict carries it.

        Returns updated (data, params) copies — never mutates in place.
        """
        logger.debug(
            "CSRF error (%s) — refreshing token (attempt %d/%d)",
            error_code or error_info,
            attempt,
            config.MAX_RETRIES,
        )
        try:
            new_token = self._refresh_csrf_token()
        except Exception as exc:
            raise CSRFError(f"Failed to refresh CSRF token: {exc}") from exc

        # Reinject into whichever dict holds the token key
        data, params = self._inject_token(new_token, data, params)
        return data, params

    @staticmethod
    def _inject_token(
        token: str, data: dict, params: dict
    ) -> tuple[dict, dict]:
        """
        Return (data, params) copies with ``token`` updated to *token*.
        Only one dict should ever carry the key; we update the first match.
        """
        for bucket_name, bucket in (("data", data), ("params", params)):
            if "token" in bucket:
                bucket = dict(bucket)
                bucket["token"] = token
                logger.debug("Injected new CSRF token into %s", bucket_name)
                if bucket_name == "data":
                    return bucket, params
                return data, bucket
        return data, params

    # ------------------------------------------------------------------
    # Protected maxlag helper
    # ------------------------------------------------------------------

    def _handle_maxlag(self, response: requests.Response, attempt: int) -> None:
        """
        Sleep for the server-requested delay (or exponential back-off).
        """
        retry_after = response.headers.get(config.MAXLAG_HEADER)
        try:
            delay = float(retry_after) if retry_after is not None else None
        except ValueError:
            delay = None

        if delay is None:
            delay = config.BACKOFF_BASE * (2 ** attempt)

        logger.debug(
            "maxlag — sleeping %.1f s (attempt %d/%d)",
            delay,
            attempt,
            config.MAX_RETRIES,
        )
        time.sleep(delay)


# ---------------------------------------------------------------------------
# CookiesClient — isolated cookie I/O (unchanged from original)
# ---------------------------------------------------------------------------


class CookiesClient:
    """Static helpers for loading and persisting LWP cookie jars."""

    @staticmethod
    def save_cookies(cj: http.cookiejar.LWPCookieJar) -> None:
        """Flush the cookie jar to disk."""
        try:
            cj.save(ignore_discard=True, ignore_expires=True)
            logger.debug("Cookies saved")
        except Exception:
            logger.exception("Failed to save cookies")

    @staticmethod
    def _make_cookiejar(cookie_path: Path) -> http.cookiejar.LWPCookieJar:
        cj = http.cookiejar.LWPCookieJar(cookie_path)
        if cookie_path.exists():
            try:
                cj.load(ignore_discard=True, ignore_expires=True)
            except Exception as exc:
                logger.error("Error loading cookies: %s", exc)
        return cj


# ---------------------------------------------------------------------------
# WikiLoginClient — business layer
# ---------------------------------------------------------------------------


class WikiLoginClient(CookiesClient, RequestsHandler):
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

        client = WikiLoginClient(lang="en", family="wikipedia",
                                 username="MyBot", password="s3cr3t")
        data = client.client_request({"action": "query", "titles": "Python"})
    """

    # Write actions that need bot=1 and assertuser injected
    _WRITE_ACTIONS: frozenset[str] = frozenset(
        {
            "edit", "create", "upload", "delete", "move",
            "wbeditentity", "wbsetclaim", "wbcreateclaim",
            "wbsetreference", "wbremovereferences", "wbsetaliases",
            "wbsetdescription", "wbsetlabel", "wbsetsitelink",
            "wbmergeitems", "wbcreateredirect",
        }
    )

    def __init__(
        self,
        lang: str,
        family: str,
        username: str,
        password: str,
        cookies_dir: Optional[str] = None,
    ) -> None:
        """
        Initialise the client, load saved cookies, and authenticate.

        Args:
            lang:        Language code, e.g. ``"en"``, ``"de"``.
            family:      Site family, e.g. ``"wikipedia"``, ``"wikidata"``.
            username:    Bot / user account name.
            password:    Account password or bot password.
            cookies_dir: Directory for cookie files; defaults to config value.
        """
        self.lang = lang
        self.family = family
        self.username = username
        self._password = password  # never log or expose

        self._cookie_path: Path = get_cookie_path(cookies_dir, family, lang, username)

        logger.debug("Creating mwclient.Site for %s.%s", lang, family)
        self.api_url = f"https://{self.lang}.{self.family}.org/w/api.php"

        try:
            self._site = mwclient.Site(f"{self.lang}.{self.family}.org")
        except mwclient.errors.InvalidSiteIdError:
            raise WikiClientError(f"Invalid site ID: {self.lang}.{self.family}")

        # Attach persisted cookies to the site's session
        self.cj = self._make_cookiejar(self._cookie_path)
        self._site.connection.cookies = self.cj

        # Authenticate if cookies alone are not enough
        if not self._site.logged_in:
            try:
                self.login()
            except LoginError:
                logger.warning(
                    "Initial login failed for %s. Will retry on first request.",
                    self.username,
                )

    # ------------------------------------------------------------------
    # RequestsHandler contract — concrete implementations
    # ------------------------------------------------------------------

    @property
    def _session(self) -> requests.Session:
        """The mwclient-managed session."""
        return self._site.connection

    def _refresh_csrf_token(self) -> str:
        """Force mwclient to fetch a fresh CSRF token from the server."""
        return self._site.get_token("csrf", force=True)

    def _on_assertnameduserfailed(self) -> None:
        """
        Session expired mid-run: nuke stale cookies and re-authenticate.
        Called by the base-class retry loop; never call directly.
        """
        logger.warning(
            "assertnameduserfailed for %s on %s.%s — clearing cookies and re-logging in",
            self.username, self.lang, self.family,
        )
        _delete_cookie_file(self._cookie_path, reason="assertnameduserfailed")
        self._do_login()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def site(self) -> mwclient.Site:
        """The underlying ``mwclient.Site`` — use for high-level wiki access."""
        return self._site

    def login(self, force: bool = False) -> None:
        """
        Authenticate the session.

        Args:
            force: Re-authenticate even if already logged in.
        """
        if force or not self._site.logged_in:
            logger.info(
                "Logging in as %s on %s.%s", self.username, self.lang, self.family
            )
            self._do_login()

    def client_request(
        self,
        params: dict,
        method: str = "post",
        files: Optional[Any] = None,
    ) -> dict:
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

        if files is not None:
            method = "post"

        # Ensure JSON response and inject write-action safety params
        params = self._enrich_params({"format": "json", **params})

        logger.debug(
            "%s %s params=%s files=%s",
            method.upper(),
            self.api_url,
            {k: ("***" if k == "token" else v) for k, v in params.items()},
            list(files.keys()) if files else None,
        )

        if method == "get":
            return self._request_with_retry(
                "GET",
                self.api_url,
                params=params,
            )
        else:
            # Fetch a CSRF token now if the caller didn't supply one.
            # The retry loop will refresh it automatically on CSRF errors.
            if "token" not in params:
                params["token"] = self._site.get_token("csrf")

            return self._request_with_retry(
                "POST",
                self.api_url,
                data=params,
                files=files,
            )

    def post_continue(
        self,
        params: dict,
        action: str,
        _p_: str = "pages",
        p_empty: Optional[Union[list, dict]] = None,
        Max: int = 500_000,
        first: bool = False,
        _p_2: str = "",
        _p_2_empty: Optional[Union[list, dict]] = None,
    ) -> Union[list, dict]:
        """
        Drive a MediaWiki API continuation query to completion.

        Iterates the ``continue`` token until all pages are fetched or *Max*
        results have been collected.

        Args:
            params:     Base API parameters.
            action:     Top-level JSON key to extract results from
                        (e.g. ``"query"``, ``"wbsearchentities"``).
            _p_:        Sub-key inside *action* (default ``"pages"``).
            p_empty:    Seed value for the accumulator (list or dict).
            Max:        Stop accumulating after this many results.
            first:      Return only the first element of the result list.
            _p_2:       Secondary sub-key when *first* is True.
            _p_2_empty: Seed for secondary accumulator.

        Returns:
            Accumulated results as a list or dict, depending on *p_empty*.
        """
        logger.debug("post_continue start. action=%s _p_=%s", action, _p_)

        if isinstance(Max, str) and Max.isdigit():
            Max = int(Max)
        if Max == 0:
            Max = 500_000

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

            body = self.client_request(page_params)

            if not body:
                logger.debug("post_continue: empty response, stopping")
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
                logger.debug("post_continue: no data in response, stopping")
                break

            logger.debug("post_continue: +%d items (total %d)", len(data), len(results))

            if Max <= len(results) > 1:
                logger.debug("post_continue: Max=%d reached, stopping", Max)
                break

            if isinstance(results, list):
                results.extend(data)
            else:
                results = {**results, **data}

        logger.debug("post_continue: done, %d total results", len(results))
        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _ensure_logged_in(self) -> None:
        """Verify the session is authenticated; attempt cookie-based revival."""
        if self._site.logged_in:
            logger.info("Session already authenticated (logged_in=%s)", self._site.logged_in)
            return
        if self._cookie_path.exists():
            try:
                self._site.site_init()
                if self._site.logged_in:
                    logger.info(
                        "Revived session via cookies as %s", self._site.username
                    )
                    return
            except Exception as exc:
                logger.error("site_init failed: %s", exc)

    def _enrich_params(self, params: dict) -> dict:
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

        if action == "query":
            params.pop("bot", None)
            params.pop("summary", None)
            return params

        is_write = (
            action in self._WRITE_ACTIONS
            or action.startswith("wb")
            or self.family == "wikidata"
        )
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
            raise LoginError(
                f"Login failed for {self.username} on {self.lang}.{self.family}: {exc}"
            ) from exc

        if self._site.logged_in:
            logger.info(
                "Logged in successfully as %s on %s.%s",
                self.username, self.lang, self.family,
            )
            self.save_cookies(self.cj)

    def __repr__(self) -> str:
        return (
            f"WikiLoginClient(lang={self.lang!r}, family={self.family!r}, "
            f"username={self.username!r})"
        )


__all__ = [
    "RequestsHandler",
    "WikiLoginClient",
]
