""" """

import datetime
import logging

logger = logging.getLogger(__name__)
Created_Cache = {}


def check_create_time(page, title_page):
    # ---
    """
    Checks if a page was created at least three hours ago before allowing bot edits.

    Returns True if the page is not in the Arabic main namespace or if the creation timestamp is missing. Returns False if the page was created less than three hours ago, caching the result for future checks.
    """
    # ---
    if title_page in Created_Cache:
        return Created_Cache[title_page]
    # ---
    ns = page.namespace()
    lang = page.lang
    # ---
    if ns != 0 or lang != "ar":
        return True
    # ---
    now = datetime.datetime.now(datetime.timezone.utc)
    # ---
    create_data = page.get_create_data()  # { "timestamp" : "2025-05-07T12:00:17Z", "user" : "", "anon" : "" }
    # ---
    delay_hours = 3
    # ---
    if create_data.get("timestamp"):
        # ---
        create_time = create_data["timestamp"]
        ts_c_time = datetime.datetime.strptime(create_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        # ---
        diff = (now - ts_c_time).total_seconds() / (60 * 60)
        # ---
        user = create_data.get("user", "")
        # ---
        wait_time = delay_hours - diff
        # ---
        if diff < delay_hours:
            logger.info(f"<<yellow>>Page:{title_page} create at ({create_time}).")
            logger.info(f"<<invert>>Page Created before {diff:.2f} hours by: {user}, wait {wait_time:.2f}H.")
            return False
    # ---
    return True


def check_last_edit_time(page, title_page, delay):
    # ---
    """
    Checks if enough time has passed since the last non-bot edit before allowing a bot to edit.

    If the last editor is a bot, editing is allowed immediately. Otherwise, returns False if the last edit was made less than the specified delay (in minutes) ago; returns True if the delay has passed or if no last edit timestamp is available.

    Args:
        page: The page object to check.
        title_page: The title of the page.
        delay: Minimum number of minutes that must have passed since the last edit.
    """
    userinfo = page.get_userinfo()
    # ---
    if "bot" in userinfo.get("groups", []):
        return True
    # ---
    # example: 2025-05-07T12:00:17Z
    timestamp = page.get_timestamp()
    # ---
    now = datetime.datetime.now(datetime.timezone.utc)
    # ---
    if timestamp:
        ts_time = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        # ---
        diff_minutes = (now - ts_time).total_seconds() / 60
        # ---
        # logger.info(f"<<grey>> last-edit Δ={diff_minutes:.2f} min for {title_page}")
        # ---
        wait_time = delay - diff_minutes
        # ---
        if diff_minutes < delay:
            logger.info(f"<<yellow>>Page:{title_page} last edit ({timestamp}).")
            logger.info(
                f"<<invert>>Page Last edit before {delay} minutes, Wait {wait_time:.2f} minutes. title:{title_page}"
            )
            return False
    # ---
    return True


__all__ = [
    "check_create_time",
    "check_last_edit_time",
]
