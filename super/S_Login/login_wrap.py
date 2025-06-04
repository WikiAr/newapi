"""

from ..super.S_Login.login_wrap import LoginWrap

# login_bot, cat_bots_login2 = LoginWrap(title, sitecode, family, bots_login_cache, User_tables)
# bots_login_cache.update(cat_bots_login2)

"""
from ...api_utils import printe
from .super_login import Login

hases = {}

def LoginWrap(title, sitecode, family, bots_login_cache, User_tables):
    # ---
    cache_key = (sitecode, family)  # Consider adding relevant kwargs to key
    # ---
    hases.setdefault(cache_key, 0)
    # ---
    if bots_login_cache.get(cache_key):
        login_bot = bots_login_cache[cache_key]
        # ---
        hases[cache_key] += 1
        # ---
        printe.output(f"### <<green>> LoginWrap has bot for ({sitecode}.{family}.org) count: {hases[cache_key]}", p=True)
    else:
        login_bot = Login(sitecode, family=family)
        # ---
        printe.output(f"### <<purple>> LoginWrap make new bot for ({sitecode}.{family}.org)", p=True)
        # ---
        login_bot.add_users({family: User_tables}, lang=sitecode)
        # ---
        bots_login_cache[cache_key] = login_bot
    # ---
    return login_bot, bots_login_cache
