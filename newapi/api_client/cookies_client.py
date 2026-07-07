""" """

from __future__ import annotations

import http.cookiejar
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CookiesClient — isolated cookie I/O (unchanged from original)
# ---------------------------------------------------------------------------


class CookiesClient:
    """Static helpers for loading and persisting LWP cookie jars."""

    @staticmethod
    def save_cookies(cj: http.cookiejar.LWPCookieJar) -> None:
        """
        Persist the current session cookies to disk immediately.

        Called automatically after every login, but you can call this manually
        to checkpoint the session after a long batch of writes.
        """
        try:
            # Save cookies to disk, ignoring discard and expire attributes
            cj.save(ignore_discard=True, ignore_expires=True)
            # Log successful cookie save operation
            logger.debug("Cookies saved to _cookie_path")
        except Exception:
            # Log any exceptions that occur during cookie saving
            logger.exception("Failed to save cookies")

    @staticmethod
    def _make_cookiejar(cookie_path: Path) -> http.cookiejar.LWPCookieJar:
        # Create a new LWPCookieJar instance with the specified path
        cj = http.cookiejar.LWPCookieJar(cookie_path)
        if cookie_path.exists():
            try:
                cj.load(ignore_discard=True, ignore_expires=True)
            except Exception as exc:
                logger.error("Error loading cookies: %s", exc)
        return cj


__all__ = [
    "CookiesClient",
]
