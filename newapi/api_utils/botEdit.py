"""
from newapi.api_utils import botEdit
bot_edit!
"""

from .bot_edit.bot_edit_by_templates import is_bot_edit_allowed

#
#
from .bot_edit.bot_edit_by_time import check_create_time, check_last_edit_time

Created_Cache = {}


def bot_May_Edit(text="", title_page="", botjob="all", page=False, delay=0):
    # ---
    """
    Determines whether a bot is permitted to edit a page based on templates, last edit time, and creation time.

    If a page object is provided and template checks pass, the function also verifies that the page was not edited or created too recently, applying namespace and language restrictions for time-based checks.

    Args:
        text: The page text to analyze for edit-blocking templates.
        title_page: The title of the page being checked.
        botjob: The bot job type, used to determine relevant template restrictions.
        page: The page object, required for time-based checks.
        delay: Minimum number of minutes since the last edit required before editing.

    Returns:
        True if the bot is allowed to edit the page; False otherwise.
    """
    check_it = is_bot_edit_allowed(text=text, title_page=title_page, botjob=botjob)
    # ---
    if page and check_it:
        # ---
        if delay and isinstance(delay, int):
            # ---
            ns = page.namespace()
            lang = page.lang
            # ---
            if ns != 0 or lang != "ar":
                return check_it
            # ---
            check_time = check_last_edit_time(page, title_page, delay)
            # ---
            if not check_time:
                return False
        # ---
        check_create = check_create_time(page, title_page)
        # ---
        Created_Cache[title_page] = check_create
        # ---
        if not check_create:
            return False
    # ---
    return check_it


def botMayEdit(**kwargs):
    return bot_May_Edit(**kwargs)


__all__ = [
    "bot_May_Edit",
]
