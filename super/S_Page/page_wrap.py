"""

from ..super.S_Page import page_wrap
# page, cat_bots_login = MainPageWrap(title, lang, family="wikipedia", cat_bots_login)

"""
# ---
from ..super.S_Page import super_page
from ..super.S_Login.super_login import Login
from ..api_utils import printe

User_tables = {}

def MainPageWrap(title, lang, family="wikipedia", cat_bots_login):
    # ---
    cache_key = (lang, family)  # Consider adding relevant kwargs to key
    # ---
    if cat_bots_login.get(cache_key):
        login_bot = cat_bots_login[cache_key]
    else:
        login_bot = Login(lang, family=family)
        # ---
        printe.output(f"<<purple>> MainPage make new bot for ({lang}.{family}.org)")
        # ---
        login_bot.add_users({family: User_tables})
        # ---
        cat_bots_login[cache_key] = login_bot
    # ---
    page = super_page.MainPage(login_bot, title, lang, family=family)
    # ---
    return page, cat_bots_logins
