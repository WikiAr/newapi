"""
TODO: should use new ALL_APIS class
"""
# ---
import os
import sys
from ..super.S_API import bot_api
from ..super.S_Category import catdepth_new

from ..super.S_Page import super_page
from ..super.login_wrap import LoginWrap
from ..api_utils.user_agent import default_user_agent
from ..api_utils import lang_codes

from ..accounts.useraccount import User_tables_bot, User_tables_ibrahem
home_dir = os.getenv("HOME")
# ---
User_tables = User_tables_bot
# ---
if "workibrahem" in sys.argv:
    User_tables = User_tables_ibrahem
    # ---
    print(f"page.py use {User_tables['username']} account.")
# ---
user_agent = default_user_agent()
# ---
change_codes = lang_codes.change_codes

logins_cache = {}


def log_it(lang, family):
    # ---
    login_bot, logins_cache2 = LoginWrap(lang, family, logins_cache, User_tables)
    # ---
    logins_cache.update(logins_cache2)
    # ---
    return login_bot


def MainPage(title, lang, family="wikipedia"):
    # ---
    login_bot = log_it(lang, family)
    # ---
    page = super_page.MainPage(login_bot, title, lang, family=family)
    # ---
    return page


def CatDepth(title, sitecode="", family="wikipedia", **kwargs):
    # ---
    login_bot = log_it(sitecode, family)
    # ---
    result = catdepth_new.subcatquery(login_bot, title, sitecode=sitecode, family=family, **kwargs)
    # ---
    return result


def NEW_API(lang="", family="wikipedia"):
    # ---
    login_bot = log_it(lang, family)
    # ---
    result = bot_api.NEW_API(login_bot, lang=lang, family=family)
    # ---
    return result


__all__ = [
    'home_dir',
    'user_agent',
    'MainPage',
    'NEW_API',
    'CatDepth',
    'change_codes',
]
