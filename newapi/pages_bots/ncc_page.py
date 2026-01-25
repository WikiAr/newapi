# ---
"""
TODO: should use new ALL_APIS class
"""

import os
# import sys
# ---
home_dir = os.getenv("HOME")
# ---
from ..super.S_API import bot_api
from ..super.S_Category import catdepth_new
from ..super.S_Page import super_page
from ..super.login_wrap import LoginWrap
from ..api_utils.user_agent import default_user_agent
from ..api_utils import lang_codes

from ..accounts.user_account_ncc import User_tables, SITECODE, FAMILY
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

def MainPage(title, lang, family=FAMILY):
    # ---
    login_bot = log_it(lang, family)
    # ---
    page = super_page.MainPage(login_bot, title, lang, family=family)
    # ---
    return page

def CatDepth(title, sitecode=SITECODE, family=FAMILY, **kwargs):
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


ncc_MainPage = MainPage

__all__ = [
    'home_dir',
    'user_agent',
    'MainPage',
    'ncc_MainPage',
    'NEW_API',
    'CatDepth',
    'change_codes',
]
