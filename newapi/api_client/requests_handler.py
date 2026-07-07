""" """

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

import mwclient
import requests

from .exceptions import (
    CSRFError,
    MaxlagError,
    WikiClientError,
)

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

    The caller injects an ``on_assertnameduserfailed`` callback at construction
    time for session-recovery logic (re-login, cookie reset).
    """

    def __init__(
        self,
        _site: mwclient.Site,
        max_retries: int = 5,
        backoff_base: int = 1,
        maxlag_header: str = "Retry-After",
        on_assertnameduserfailed: Callable[[], None] | None = None,
    ) -> None:
        self._site = _site

        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.maxlag_header = maxlag_header
        self._on_assertnameduserfailed = on_assertnameduserfailed or self._on_assertnameduserfailed_default

    # ------------------------------------------------------------------
    # Abstract-ish contract that subclasses must satisfy
    # ------------------------------------------------------------------

    @property
    def _session(self) -> requests.Session:
        """The mwclient-managed session."""
        return self._site.connection

    def _refresh_csrf_token(self) -> str:
        """Force mwclient to fetch a fresh CSRF token from the server."""
        return self._site.get_token("csrf", force=True)

    @staticmethod
    def _on_assertnameduserfailed_default() -> None:
        raise NotImplementedError  # pragma: no cover

    # ------------------------------------------------------------------
    # Retry loop  (called by WikiLoginClient.client_request)
    # ------------------------------------------------------------------

    def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        params: dict | None = None,
        data: dict | None = None,
        files: Any | None = None,
        assertnameduser_retries: int = 1,
    ) -> dict[str, Any]:
        """
        Execute a request and automatically retry on transient API errors.

        Retry conditions (each counted against ``settings.mediawiki.max_retries``):
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

        while attempt < self.max_retries:
            try:
                # TODO: handle HTTPError: 429 Client Error: Too Many Requests
                response = self._session.request(
                    method,
                    url,
                    params=working_params or None,
                    data=working_data or None,
                    files=files,
                )
                response.raise_for_status()
            except Exception as e:
                logger.error("Request failed: %s", e)
                raise

            # Non-JSON responses (e.g. uploads returning HTML) go straight back
            content_type = response.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                return {}

            try:
                body: dict[str, Any] = response.json()
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
                if attempt >= self.max_retries:
                    raise CSRFError(
                        f"CSRF token remained invalid after {self.max_retries} "
                        f"attempts. Last error: {error_info or error_code}"
                    )
                working_data, working_params = self._handle_csrf(
                    error_code,
                    error_info,
                    attempt,
                    working_data,
                    working_params,
                )
                continue

            # ── maxlag ────────────────────────────────────────────────────
            if error_code == "maxlag":
                attempt += 1
                if attempt >= self.max_retries:
                    raise MaxlagError(f"Server maxlag not resolved after {self.max_retries} attempts.")
                self._handle_maxlag(response, attempt)
                continue

            # ── assertnameduserfailed ─────────────────────────────────────
            if error_code == "assertnameduserfailed":
                if named_user_attempts >= assertnameduser_retries:
                    raise WikiClientError("assertnameduserfailed persists after re-login")
                named_user_attempts += 1
                logger.warning(
                    "assertnameduserfailed — attempting recovery (try %d/%d)",
                    named_user_attempts,
                    assertnameduser_retries,
                )
                self._on_assertnameduserfailed()
                # Reset the retry counter so maxlag/csrf budget is fresh
                attempt = 0
                # Refresh CSRF token — the old one is tied to the expired session
                try:
                    new_token = self._refresh_csrf_token()
                    working_data, working_params = self._inject_token(new_token, working_data, working_params)
                except Exception:
                    logger.debug("Could not refresh CSRF token after re-login — next error will retry")
                continue

            # ── ratelimited ───────────────────────────────────────────────
            if error_code == "ratelimited":
                attempt += 1
                if attempt >= self.max_retries:
                    raise WikiClientError(f"Ratelimit persists after {self.max_retries} attempts.")
                sleep_time = 3
                time.sleep(sleep_time)
                logger.warning("ratelimited — sleeping for %d seconds before retrying", sleep_time)
                continue

            # ── any other error — let the caller decide ───────────────────
            raise WikiClientError(f"API error {error_code}: {error_info}")

        raise MaxlagError(f"Exceeded {self.max_retries} retries without a successful response.")

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
            self.max_retries,
        )
        try:
            new_token = self._refresh_csrf_token()
        except Exception as exc:
            raise CSRFError(f"Failed to refresh CSRF token: {exc}") from exc

        # Reinject into whichever dict holds the token key
        data, params = self._inject_token(new_token, data, params)
        return data, params

    @staticmethod
    def _inject_token(token: str, data: dict, params: dict) -> tuple[dict, dict]:
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
        retry_after = response.headers.get(self.maxlag_header)
        try:
            delay = float(retry_after) if retry_after is not None else None
        except ValueError:
            delay = None

        if delay is None:
            delay = self.backoff_base * (2**attempt)

        logger.debug(
            "maxlag — sleeping %.1f s (attempt %d/%d)",
            delay,
            attempt,
            self.max_retries,
        )
        time.sleep(delay)


__all__ = [
    "RequestsHandler",
]
