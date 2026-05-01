"""

Examples::

client = WikiLoginClient(
    lang="en",
    family="wikipedia",
    username="MyBot",
    password="s3cr3t",
)
# Simple read
data = client.client_request({"action": "query", "titles": "Python"})

# Write — POST with auto CSRF + retry handling
data = client.client_request(
    {
        "action": "edit",
        "title": "Sandbox",
        "text": "hello",
        "summary": "test",
        "token": client.site.get_token("csrf"),
    },
    method="post",
)
"""

import copy
import http.cookiejar
import logging
from pathlib import Path
from typing import Any, Optional, Union

import mwclient
import mwclient.errors
import requests

from .cookies import (
    _delete_cookie_file,
    get_cookie_path,
)
from .exceptions import LoginError, WikiClientError
from .requests_handler import wrap_session

logger = logging.getLogger(__name__)


class CookiesClient:

    @staticmethod
    def save_cookies(cj) -> None:
        """
        Persist the current session cookies to disk immediately.

        Called automatically after every login, but you can call this manually
        to checkpoint the session after a long batch of writes.
        """
        try:
            cj.save(ignore_discard=True, ignore_expires=True)
            logger.debug("Cookies saved to _cookie_path")
        except Exception as e:
            logger.exception("Failed to save cookies")

    @staticmethod
    def _make_cookiejar(cookie_path) -> http.cookiejar.LWPCookieJar:
        cj = http.cookiejar.LWPCookieJar(cookie_path)

        if cookie_path.exists():
            try:
                cj.load(ignore_discard=True, ignore_expires=True)
            except Exception as e:
                logger.error("Error loading cookies: %s", e)
        return cj


class WikiLoginClient(CookiesClient):
    """
    A thin wrapper around mwclient.Site that:

    - Persists the session across script runs via a Mozilla cookie jar.
    - Skips the login round-trip when saved cookies are still valid.
    - Transparently retries requests on CSRF errors and server maxlag.
    - Recovers automatically if the session expires mid-run
      (assertnameduserfailed).
    - Injects bot=1 and assertuser into all write-action requests.
    - Reuses the same requests.Session across instances for the same wiki+user.

    Usage
    -----
        client = WikiLoginClient(
            lang="en",
            family="wikipedia",
            username="MyBot",
            password="s3cr3t",
        )
        page = client.site.pages["Python"]
        print(page.text())

        # Direct API call
        data = client.client_request({"action": "query", "titles": "Python"})

    The `site` property exposes the full mwclient.Site API.
    """

    # Write actions that need bot=1 and assertuser injected
    _WRITE_ACTIONS = {
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

    def __init__(
        self,
        lang: str,
        family: str,
        username: str,
        password: str,
        cookies_dir: Optional[str] = None,
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

        # ── Cookie path ────────────────────────────────────────────────────
        self._cookie_path: Path = get_cookie_path(cookies_dir, family, lang, username)

        # ── mwclient Site ──────────────────────────────────────────────────
        logger.debug("Creating mwclient.Site for %s.%s", lang, family)

        self.api_url = f"https://{self.lang}.{self.family}.org/w/api.php"

        try:
            self._site = mwclient.Site(f"{self.lang}.{self.family}.org")
        except mwclient.errors.InvalidSiteIdError:
            raise WikiClientError(f"Invalid site ID: {self.lang}.{self.family}")

        # ── Inject saved cookies ───────────────────────────────────────────
        # mwclient stores its requests.Session at site.connection.
        self.cj = self._make_cookiejar(self._cookie_path)
        self._site.connection.cookies = self.cj

        # ── Wrap the session with retry / CSRF / maxlag logic ──────────────
        wrap_session(self._site.connection, self._site)

        # ── Authenticate if necessary ──────────────────────────────────────
        if not self._site.logged_in:
            try:
                self.login()
            except LoginError:
                logger.warning("Initial login failed for %s. Will retry on first request.", self.username)

    # ── Public properties ──────────────────────────────────────────────────

    @property
    def site(self) -> mwclient.Site:
        """The underlying mwclient.Site — use this to interact with the wiki."""
        return self._site

    # ── Public methods ─────────────────────────────────────────────────────

    def login(self, force: bool = False) -> None:
        """
        Authenticate the session.

        Args:
            force: If True, forces a fresh login regardless of current status.
        """
        if force or not self._site.logged_in:
            logger.info("Logging in as %s on %s.%s", self.username, self.lang, self.family)
            self._do_login()

    def client_request(
        self,
        params: dict,
        method: str = "post",
        files: Optional[Any] = None,
    ) -> dict:
        """
        Send a GET or POST request to the wiki API and return the parsed JSON.

        This is the low-level escape hatch for callers that need to hit the API
        directly without going through mwclient's higher-level helpers. The
        session's retry wrapper (CSRF refresh, maxlag backoff) is active on
        every call made through this method.

        Args:
            params: MediaWiki API parameters as a plain dict.
                    ``action`` and ``format`` are required by the API;
                    ``format`` defaults to ``"json"`` if not supplied.
            method: ``"get"`` (default) or ``"post"``. Case-insensitive.
                    Use POST for any write operation (edits, uploads, etc.)
                    or when the payload may exceed URL length limits.
            files:  Optional dict of ``{field_name: file-like object}`` for
                    multipart uploads (e.g. ``{"file": open("image.png","rb")}``).
                    Automatically forces the method to POST when supplied.

        Returns:
            Parsed JSON response as a dict.

        Raises:
            ValueError:         If *method* is not ``"get"`` or ``"post"``.
            WikiClientError:    Wraps API-level errors (code + info message).
                                Note: CSRF and maxlag are handled transparently
                                by the session wrapper before reaching here.
            requests.HTTPError: On non-2xx HTTP responses.

        """
        method = method.lower()
        if method not in ("get", "post"):
            raise ValueError(f"method must be 'get' or 'post', got {method!r}")

        # Files can only travel via multipart POST
        if files is not None:
            method = "post"

        # Always request JSON unless the caller explicitly overrides
        params = {"format": "json", **params}

        # Merge #5: inject bot flag and identity assertion for write actions
        params = self._enrich_params(params)

        session: requests.Session = self._site.connection

        logger.debug(
            "%s %s params=%s files=%s",
            method.upper(),
            self.api_url,
            # Never log token values
            {k: ("***" if k == "token" else v) for k, v in params.items()},
            list(files.keys()) if files else None,
        )

        # Merge #4: assertnameduserfailed recovery — retry once after re-login
        for attempt in range(2):
            if method == "get":
                response = session.request("GET", self.api_url, params=params)
            else:
                if "token" not in params:
                    params["token"] = self._site.get_token("csrf")
                response = session.request("POST", self.api_url, data=params, files=files)

            response.raise_for_status()

            result: dict = response.json()

            error = result.get("error", {})
            if not error:
                return result

            error_code = error.get("code", "")
            error_info = error.get("info", error)

            # ── assertnameduserfailed: session expired silently mid-run ────
            # Matches super_login.py post_it_parse_data recovery logic.
            if error_code == "assertnameduserfailed":
                if attempt == 0:
                    logger.warning(
                        "assertnameduserfailed for %s on %s.%s — clearing cookies and re-logging in",
                        self.username,
                        self.lang,
                        self.family,
                    )
                    # Nuke the stale cookie file and the cached session
                    _delete_cookie_file(self._cookie_path, reason="assertnameduserfailed")
                    self._do_login()
                    continue  # retry the original request
                else:
                    raise WikiClientError(
                        f"assertnameduserfailed persists after re-login for "
                        f"{self.username} on {self.lang}.{self.family}"
                    )

            # All other errors — surface to the caller
            raise WikiClientError(f"API error {error_code}: {error_info}")

        # Should never be reached
        return {}

    # ── Private helpers ────────────────────────────────────────────────────

    def _ensure_logged_in(self) -> None:
        """
        Check whether the current session is authenticated.
        """
        if self._site.logged_in:
            logger.info(f"Session already authenticated {self._site.logged_in=}")
            return
        if self._cookie_path.exists():
            try:
                self._site.site_init()
                if self._site.logged_in:
                    print(f"{self._site.logged_in=}")
                    print(f"{self._site.username=}")
                    return
            except Exception as e:
                logger.error("Error in site_init: %s", e)

        # if not self._site.logged_in: self._do_login()
        # don't login yet, user can use login() method

    def _enrich_params(self, params: dict) -> dict:
        """
        Merge #5: inject write-action safety params.

        For any action that modifies wiki content:
          - ``bot=1``        marks edits as bot edits in the recent-changes log.
          - ``assertuser``   makes the API reject the request if the session
                             user doesn't match, preventing accidental edits
                             under the wrong account.

        Read-only actions (query, etc.) are left untouched.
        Also cleans up query params that don't belong in write requests
        (matches your old filter_params / params_w logic).
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
        Perform the mwclient login handshake and persist the resulting cookies.

        Raises:
            LoginError: if mwclient rejects the credentials.
        """
        try:
            self._site.login(self.username, self._password)
        except mwclient.errors.LoginError as exc:
            raise LoginError(f"login failed for {self.username} on {self.lang}.{self.family}: {exc}") from exc

        if self._site.logged_in:
            logger.info(
                "Logged in successfully as %s on %s.%s",
                self.username,
                self.lang,
                self.family,
            )
            self.save_cookies(self.cj)

    def post_continue(
        self,
        params: dict,
        action: str,
        _p_: str = "pages",
        p_empty: Optional[Union[list, dict]] = None,
        Max: int = 500000,
        first: bool = False,
        _p_2: str = "",
        _p_2_empty: Optional[Union[list, dict]] = None,
    ) -> Union[list, dict]:
        """
        Handles MediaWiki API continuation queries.
        Should mimic behavior of old Login.post_continue.
        """
        logger.debug("_______________________")
        logger.debug(f", start. {action=}, {_p_=}")

        if isinstance(Max, str) and Max.isdigit():
            Max = int(Max)

        if Max == 0:
            Max = 500000

        p_empty = p_empty if p_empty is not None else []
        _p_2_empty = _p_2_empty if _p_2_empty is not None else []

        results = p_empty
        continue_params = {}
        d = 0

        while continue_params != {} or d == 0:
            params2 = copy.deepcopy(params)
            d += 1

            if continue_params:
                logger.debug("continue_params:")
                for k, v in continue_params.items():
                    params2[k] = v
                logger.debug(params2)

            json1 = self.client_request(params2)

            if not json1:
                logger.debug(", json1 is empty. break")
                break

            continue_params = {}

            if action == "wbsearchentities":
                data = json1.get("search", [])
            else:
                continue_params = json1.get("continue", {})
                data = json1.get(action, {}).get(_p_, p_empty)

                if _p_ == "querypage":
                    data = data.get("results", [])
                elif first:
                    if isinstance(data, list) and len(data) > 0:
                        data = data[0]
                        if _p_2:
                            data = data.get(_p_2, _p_2_empty)

            if not data:
                logger.debug("post continue, data is empty. break")
                break

            logger.debug(f"post continue, len:{len(data)}, all: {len(results)}")

            if Max <= len(results) and len(results) > 1:
                logger.debug(f"post continue, {Max=} <= {len(results)=}. break")
                break

            if isinstance(results, list):
                results.extend(data)
            else:
                results = {**results, **data}

        logger.debug(f"post continue, {len(results)=}")
        return results

    def __repr__(self) -> str:
        return f"WikiLoginClient(lang={self.lang!r}, family={self.family!r}, username={self.username!r})"


__all__ = [
    "WikiLoginClient",
]
