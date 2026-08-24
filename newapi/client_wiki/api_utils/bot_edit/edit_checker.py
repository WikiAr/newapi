""" """

from __future__ import annotations

import logging
from typing import Any

from ....config import main_settings
from .bot_edit_by_templates import is_bot_edit_allowed
from .bot_edit_by_time import check_create_time, check_last_edit_time

logger = logging.getLogger(__name__)


def is_page_editable(
    text: str = "",
    title_page: str = "",
    bot_script: str = "all",
    page_data: dict[str, Any] | None = None,
    delay: int | Any = 0,
    use_cache: bool = True,
) -> bool:
    """
    Determines whether a bot is permitted to edit a page based on templates, last edit time, and creation time.
    """
    page_data = page_data or {}

    if (main_settings.bot.force_edit) or main_settings.bot.workibrahem:
        return True

    check_it = is_bot_edit_allowed(
        text=text,
        title_page=title_page,
        bot_script=bot_script,
        use_cache=use_cache,
    )

    ns = page_data.get("ns")
    lang = page_data.get("lang")
    timestamp = page_data.get("timestamp", "")
    userinfo = page_data.get("userinfo") or {}

    if page_data and check_it:
        if delay and isinstance(delay, int):
            if ns != 0 or lang != "ar":
                return check_it

            # check last edit time
            check_time = check_last_edit_time(
                title_page,
                delay,
                userinfo=userinfo,
                timestamp=timestamp,
            )
            if not check_time:
                return False

        check_create = check_create_time(page_data, title_page)

        if not check_create:
            return False

    return check_it


__all__ = [
    "is_page_editable",
]
