# api_client/requests_handler.py
# Wraps the requests.Session used internally by mwclient.Site so that every
# API call gets automatic CSRF token refresh and maxlag backoff — transparently,
# with no changes needed in calling code.

import logging
import time
from typing import Callable

import requests

from . import config
from .exceptions import CSRFError, MaxlagError

logger = logging.getLogger(__name__)


def _replace_token(kwargs: dict, new_token: str) -> dict:
    """
    Return a copy of *kwargs* with any "token" key updated to *new_token*.

    mwclient passes write parameters either in `params` (GET query string) or
    `data` (POST body).  We update whichever dict contains the key.
    """
    kwargs = dict(kwargs)  # shallow copy — don't mutate caller's dict

    for key in ("params", "data"):
        bucket = kwargs.get(key)
        if isinstance(bucket, dict) and "token" in bucket:
            bucket = dict(bucket)  # copy the inner dict too
            bucket["token"] = new_token
            kwargs[key] = bucket
            logger.debug("Injected new CSRF token into request %s", key)
            break

    return kwargs


def wrap_session(session: requests.Session, site) -> None:
    """
    Monkey-patch *session*.request so that every HTTP call made by mwclient
    is intercepted and retried when needed.

    The original session.request method is preserved as session._original_request
    so the wrapper can delegate to it.

    Args:
        session: The requests.Session stored at site.connection.
        site:    The mwclient.Site instance (used to force-refresh CSRF tokens).
    """
    # Guard against double-wrapping
    if hasattr(session, "_original_request"):
        logger.debug("Session already wrapped — skipping")
        return

    original_request: Callable = session.request
    session._original_request = original_request

    def _wrapped_request(method: str, url: str, **kwargs):
        """
        Retry wrapper around requests.Session.request.

        Retry conditions (each counted against MAX_RETRIES):
          - CSRF / bad token  → force-refresh token, inject into request, retry
          - maxlag            → sleep with exponential backoff, retry

        All other errors are re-raised immediately without retrying.
        """
        attempt = 0

        while attempt < config.MAX_RETRIES:
            response: requests.Response = original_request(method, url, **kwargs)

            # Only inspect JSON responses — pass everything else straight through
            content_type = response.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                return response

            try:
                body = response.json()
            except ValueError:
                # Not valid JSON despite the content-type; just return it
                return response

            error = body.get("error", {})
            error_code = error.get("code", "")
            error_info = error.get("info", "")

            # ----------------------------------------------------------------
            # CSRF / bad token
            # ----------------------------------------------------------------
            is_csrf = error_code in ("badtoken", "notoken") or error_info == "Invalid CSRF token."

            if is_csrf:
                attempt += 1
                if attempt >= config.MAX_RETRIES:
                    raise CSRFError(
                        f"CSRF token remained invalid after {config.MAX_RETRIES} "
                        f"attempts. Last error: {error_info or error_code}"
                    )

                logger.debug(
                    "CSRF error (%s) — refreshing token (attempt %d/%d)",
                    error_code or error_info,
                    attempt,
                    config.MAX_RETRIES,
                )

                # Force mwclient to fetch a fresh CSRF token
                try:
                    new_token = site.get_token("csrf", force=True)
                except Exception as exc:
                    raise CSRFError(f"Failed to refresh CSRF token: {exc}") from exc

                # Inject the new token wherever "token" appears in the request
                kwargs = _replace_token(kwargs, new_token)
                continue  # retry with the new token

            # ----------------------------------------------------------------
            # Maxlag
            # ----------------------------------------------------------------
            if error_code == "maxlag":
                attempt += 1
                if attempt >= config.MAX_RETRIES:
                    raise MaxlagError(f"Server maxlag not resolved after {config.MAX_RETRIES} attempts.")

                # Honour the server's Retry-After hint if present, else backoff
                retry_after = response.headers.get(config.MAXLAG_HEADER)
                if retry_after is not None:
                    try:
                        delay = float(retry_after)
                    except ValueError:
                        delay = config.BACKOFF_BASE * (2**attempt)
                else:
                    delay = config.BACKOFF_BASE * (2**attempt)

                logger.debug(
                    "Maxlag — sleeping %.1f s (attempt %d/%d)",
                    delay,
                    attempt,
                    config.MAX_RETRIES,
                )
                time.sleep(delay)
                continue  # retry after backoff

            # ----------------------------------------------------------------
            # assertnameduserfailed
            # ----------------------------------------------------------------
            if error_code == "assertnameduserfailed":
                attempt += 1
                if attempt >= config.MAX_RETRIES:
                    raise CSRFError(f"Session assertion failed after {config.MAX_RETRIES} attempts.")

                logger.debug(
                    "assertnameduserfailed — retrying (attempt %d/%d)",
                    attempt,
                    config.MAX_RETRIES,
                )
                delay = config.BACKOFF_BASE * (2 ** attempt)
                time.sleep(delay)
                # TODO: del cookies file, create new session, site login

                continue  # retry after backoff

            # ----------------------------------------------------------------

            # ----------------------------------------------------------------
            # No retryable error — return the response as-is
            # ----------------------------------------------------------------
            return response

        # Should not be reached, but satisfies type checkers
        raise MaxlagError(f"Exceeded {config.MAX_RETRIES} retries without a successful response.")

    session.request = _wrapped_request
    logger.debug("Session wrapped with retry handler")


__all__ = [
    "wrap_session",
]
