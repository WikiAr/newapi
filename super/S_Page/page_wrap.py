"""

from ..super.S_Page.page_wrap import MainPageWrap

# page, cat_bots_login2 = MainPageWrap(title, lang, family, cat_bots_login, User_tables)
# cat_bots_login.update(cat_bots_login2)

"""
# ---
from . import super_page
from ..S_Login.super_login import Login
from ...api_utils import printe

hases = {}

def MainPageWrap(title, lang, family, cat_bots_login, User_tables):
    # ---
    cache_key = (lang, family)  # Consider adding relevant kwargs to key
    # ---
    hases.setdefault(cache_key, 0)
    # ---
    if cat_bots_login.get(cache_key):
        login_bot = cat_bots_login[cache_key]
        # ---
        hases[cache_key] += 1
        # ---
        printe.output(f"### <<green>> MainPageWrap has bot for ({lang}.{family}.org) count: {hases[cache_key]}")
    else:
        login_bot = Login(lang, family=family)
        # ---
        printe.output(f"### <<purple>> MainPageWrap make new bot for ({lang}.{family}.org)")
        # ---
        login_bot.add_users({family: User_tables}, lang=lang)
        # ---
        cat_bots_login[cache_key] = login_bot
    # ---
    page = super_page.MainPage(login_bot, title, lang, family=family)
    # ---
    return page, cat_bots_login
