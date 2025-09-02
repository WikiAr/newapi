"""
from newapi import toolforge_page
# ---
User_tables_md = {
    "username": medwiki_account.username,
    "password": medwiki_account.password,
}
# ---
toolforge_page.add_User_table(User_tables_md, "toolforge", "medwiki")
# ---
CatDepth = toolforge_page.subcatquery
MainPage = toolforge_page.MainPage(title, lang, family="toolforge")
# ---
"""
# ---
from ..super.S_Category import catdepth_new

from ..super.S_API import bot_api
from ..super.S_Page import super_page
from ..super.login_wrap import LoginWrap

User_tables = {}
logins_cache = {}

def add_User_table(table, family, lang):
    # ---
    User_tables[(lang, family)] = table
    User_tables[("*", family)] = table

def log_it(lang, family):
    # ---
    table = User_tables.get((lang, family)) or User_tables.get(("*", family))
    # ---
    login_bot, logins_cache2 = LoginWrap(lang, family, logins_cache, table)
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
    # "bot_api",
    # "super_page",
    "catdepth_new",
    "MainPage",
    "add_User_table",
    "CatDepth",
]
