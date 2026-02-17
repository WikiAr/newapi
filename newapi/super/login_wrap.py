"""

from newapi import LoginWrap

from .super.login_wrap import LoginWrap

# login_bot, catbots_login2 = LoginWrap(sitecode, family, bots_login_cache, User_tables)
# bots_login_cache.update(catbots_login2)

"""

import logging

from .super_login import Login

logger = logging.getLogger(__name__)

hases = {}


def LoginWrap(sitecode, family, bots_login_cache, User_tables):
    # ---
    cache_key = (sitecode, family)  # Consider adding relevant kwargs to key
    # ---
    username = User_tables.get("username")
    # ---
    if username:
        cache_key = (sitecode, family, username)
    # ---
    hases.setdefault(cache_key, 0)
    # ---
    if bots_login_cache.get(cache_key):
        login_bot = bots_login_cache[cache_key]
        # ---
        hases[cache_key] += 1
        # ---
        if hases[cache_key] % 100 == 0:
            logger.info(
                f"### <<green>> LoginWrap has bot for ({sitecode}.{family}.org|{username}) count: {hases[cache_key]}"
            )
    else:
        login_bot = Login(sitecode, family=family)
        # ---
        logger.info(f"### <<purple>> LoginWrap make new bot for ({sitecode}.{family}.org|{username})")
        # ---
        login_bot.add_users({family: User_tables}, lang=sitecode)
        # ---
        bots_login_cache[cache_key] = login_bot
    # ---
    return login_bot, bots_login_cache
