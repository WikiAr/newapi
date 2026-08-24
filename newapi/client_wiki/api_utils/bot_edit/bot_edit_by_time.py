""" """

from __future__ import annotations

import datetime
import logging
from typing import Any

logger = logging.getLogger(__name__)

_created_cache = {}


def check_create_time(
    page_data: dict[str, Any],
    title_page: str,
) -> bool:
    """
    Checks if a page was created at least three hours ago before allowing bot edits.

    Returns True if the page is not in the Arabic main namespace or if the creation timestamp is missing.
    Returns False if the page was created less than three hours ago, caching the result for future checks.
    """
    if title_page in _created_cache:
        return _created_cache[title_page]

    ns = page_data.get("ns")
    lang = page_data.get("lang")
    create_data = page_data.get("create_data") or {}

    if ns != 0 or lang != "ar":
        _created_cache[title_page] = True
        return True

    # load times
    now = datetime.datetime.now(datetime.UTC)

    # delay_hours
    delay_hours = 3

    if create_data.get("timestamp"):
        create_time = create_data["timestamp"]
        ts_c_time = datetime.datetime.strptime(create_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.UTC)

        diff = (now - ts_c_time).total_seconds() / (60 * 60)

        user = create_data.get("user", "")

        wait_time = delay_hours - diff

        if diff < delay_hours:
            logger.debug(f"Page:{title_page} create at ({create_time}).")
            logger.debug(f"Page Created before {diff:.2f} hours by: {user}, wait {wait_time:.2f}H.")
            return False

    _created_cache[title_page] = True
    return True


def check_last_edit_time(
    title_page: str,
    delay: int,
    userinfo: dict[str, Any],
    timestamp: str,
) -> bool:
    """
    Checks if enough time has passed since the last non-bot edit before allowing a bot to edit.
    """

    if "bot" in userinfo.get("groups", []):
        return True

    # example: 2025-05-07T12:00:17Z
    now = datetime.datetime.now(datetime.UTC)

    if timestamp:
        ts_time = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.UTC)
        diff_minutes = (now - ts_time).total_seconds() / 60
        wait_time = delay - diff_minutes
        if diff_minutes < delay:
            logger.debug(f"Page:{title_page} last edit ({timestamp}), delay: {delay}.")
            logger.debug(f"Wait {wait_time:.2f} minutes. title:{title_page}")
            return False

    return True


__all__ = [
    "check_create_time",
    "check_last_edit_time",
]
