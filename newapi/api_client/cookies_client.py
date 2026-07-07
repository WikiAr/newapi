""" """

from __future__ import annotations

import http.cookiejar
import logging
import os
import stat
from datetime import datetime, timedelta
from pathlib import Path

import mwclient

logger = logging.getLogger(__name__)

# Cookie files older than this are treated as stale and deleted before loading.
_COOKIE_MAX_AGE_DAYS = 3


def get_cookies_dir() -> str:
    """Load configuration from environment variables."""
    cookies_dir = os.getenv("COOKIES_DIR") or "~/tmp/cookies"
    cookies_dir = os.path.expandvars(cookies_dir)
    try:
        cookies_dir = Path(str(cookies_dir)).expanduser()
    except Exception as e:
        logger.error(f"Error expanding cookies directory: {e}")

    return str(cookies_dir)


def get_cookie_path(
    cookies_dir: str | None,
    family: str,
    lang: str,
    username: str,
) -> Path:
    """
    Return the cookie file path for the given site + user combination.

    Base directory resolution order (mirrors your old cookies_bot.py):
      1. *cookies_dir* if explicitly passed.
      2. $HOME/cookies/ if the HOME env var is set.
      3. A cookies/ folder next to this file as a last resort.

    Convention: {cookies_dir}/{family}_{lang}_{username}.mozilla
    Example:    ~/cookies/wikipedia_en_mybot.mozilla

    The directory is created if it does not already exist.
    Normalisation: family, lang, and the base part of username are lowercased;
    spaces replaced with underscores; bot-password suffix (@...) stripped.
    """
    # ── Resolve base directory ─────────────────────────────────────────────
    if cookies_dir is None:
        cookies_dir = get_cookies_dir()

    base = Path(cookies_dir)

    base.mkdir(parents=True, exist_ok=True)

    # Set group-readable permissions on the directory (matches old chmod logic)
    try:
        os.chmod(base, stat.S_IRWXU | stat.S_IRWXG)
    except OSError as exc:
        logger.debug("Could not chmod cookies dir %s: %s", base, exc)

    logger.info("cookie path: %s", base)

    # ── Normalise filename components ──────────────────────────────────────
    family = family.lower()
    lang = lang.lower()
    # Strip bot-password suffix (e.g. "MyBot@BotPassword" -> "mybot")
    username = username.lower().replace(" ", "_").split("@")[0]

    file_path = base / f"{family}_{lang}_{username}.mozilla"
    logger.debug("resolved cookie file: %s", file_path)

    # ── Stale / empty file guard (from your check_if_file_is_old) ─────────
    _delete_if_stale(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    return file_path


def _delete_if_stale(path: Path) -> None:
    """
    Delete the cookie file if it is zero-bytes or older than _COOKIE_MAX_AGE_DAYS.

    Silently does nothing if the file does not exist.
    """
    if not path.exists():
        return

    # Zero-byte file is useless
    if path.stat().st_size == 0:
        _delete_cookie_file(path, reason="zero-byte file")
        return

    # File too old — the session it contains has almost certainly expired
    age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
    if age > timedelta(days=_COOKIE_MAX_AGE_DAYS):
        _delete_cookie_file(path, reason=f"older than {_COOKIE_MAX_AGE_DAYS} days ({age.days}d)")


def _delete_cookie_file(path: Path, reason: str = "") -> None:
    """Delete a cookie file, logging the outcome."""
    try:
        path.unlink(missing_ok=True)
        logger.debug("Deleted stale cookie file %s (%s)", path, reason)
    except OSError as exc:
        logger.exception("Could not delete cookie file %s: %s", path, exc)


# ---------------------------------------------------------------------------
# CookiesClient — isolated cookie I/O (unchanged from original)
# ---------------------------------------------------------------------------


class CookiesClient:
    """Static helpers for loading and persisting LWP cookie jars."""

    def __init__(
        self,
        lang: str,
        family: str,
        username: str,
        cookies_dir: str | None,
        use_cookies: None | bool = None,
    ) -> None:
        self.lang = lang
        self.family = family
        self.username = username
        self.cookies_dir = cookies_dir
        self.use_cookies = use_cookies

        self.cj = None
        self._cookie_path: None | Path = None
        if use_cookies:
            self._cookie_path = self.get_cookies_path()
            self.cj = self._make_cookiejar()

    def is_cookie_path_exists(self) -> bool:
        if self._cookie_path:
            return self._cookie_path.exists()

        return False

    def delete_cookie_file(self, reason="") -> None:
        if self.use_cookies:
            self._delete_cookie_file(self._cookie_path, reason=reason)

    def set_site_cookies(self, site: mwclient.Site) -> None:
        if self.use_cookies and self.cj:
            site.connection.cookies = self.cj  # type: ignore

    def save_cookies_cj(self) -> None:
        if self.use_cookies and self.cj:
            self.save_cookies(self.cj)

    @property
    def cookie_path(self) -> None | Path:
        return self._cookie_path

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

    def _make_cookiejar(self) -> http.cookiejar.LWPCookieJar:
        # Create a new LWPCookieJar instance with the specified path
        cj = http.cookiejar.LWPCookieJar(self._cookie_path)
        if self.is_cookie_path_exists():
            try:
                cj.load(ignore_discard=True, ignore_expires=True)
            except Exception as exc:
                logger.error("Error loading cookies: %s", exc)
        return cj

    def _delete_cookie_file(self, path: Path, reason: str = "") -> None:
        return _delete_cookie_file(path, reason)

    def get_cookies_path(self) -> Path:
        return get_cookie_path(self.cookies_dir, self.family, self.lang, self.username)


__all__ = [
    "CookiesClient",
    "get_cookie_path",
]
