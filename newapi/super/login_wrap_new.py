"""

from newapi import LoginWrap

from .super.login_wrap import LoginWrap

# login_bot = LoginWrap(sitecode, family, User_tables)

"""

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)
from .super_login import Login


@lru_cache(maxsize=128)
def _create_login_bot(sitecode, family, username, password):
    """
    Create and cache a login bot instance.

    Note: The log message inside this function will only appear on cache misses
    (i.e., when a new bot is created). This is intentional - on cache hits,
    the same bot instance is returned without logging.
    """
    logger.info(
        f"### <<purple>> LoginWrap make new bot for ({sitecode}.{family}.org|{username})"
    )
    # ---
    login_bot = Login(sitecode, family=family)
    # ---
    User_tables = {"username": username, "password": password}
    login_bot.add_users({family: User_tables}, lang=sitecode)
    # ---
    return login_bot


def LoginWrap(sitecode, family, bots_login_cache, User_tables):
    """
    Get or create a cached login bot.

    Note: bots_login_cache parameter is kept for backward compatibility but is no longer used.
    The caching is now handled by functools.lru_cache.
    """
    username = User_tables.get("username", "")
    password = User_tables.get("password", "")
    # ---
    login_bot = _create_login_bot(sitecode, family, username, password)
    # ---
    cache_info = _create_login_bot.cache_info()
    if cache_info.hits > 0 and cache_info.hits % 100 == 0:
        logger.info(
            f"### <<green>> LoginWrap has bot for ({sitecode}.{family}.org|{username}) count: {cache_info.hits}"
        )
    # ---
    # Return bots_login_cache for backward compatibility
    return login_bot, bots_login_cache
