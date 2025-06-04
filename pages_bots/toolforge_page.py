"""
from newapi import toolforge_page
# ---
User_tables_md = {
    "username": medwiki_account.username,
    "password": medwiki_account.password,
}
# ---
toolforge_page.add_Usertables(User_tables_md, "toolforge", "medwiki")
# ---
CatDepth = toolforge_page.subcatquery
MainPage = toolforge_page.MainPage(title, lang, family="toolforge")
# ---
"""
# ---
from ..super.S_Category import catdepth_new

from ..super.S_Page import super_page
from ..super.S_Login.login_wrap import LoginWrap

User_tables = {}

def add_Usertables(table, family, lang):
    # ---
    User_tables[(lang, family)] = table
    User_tables[("*", family)] = table
    # ---
    catdepth_new.add_Usertables(table, family)

logins_cache = {}

def MainPage(title, lang, family="wikipedia"):
    # ---
    table = User_tables.get((lang, family)) or User_tables.get(("*", family))
    # ---
    login_bot, logins_cache2 = LoginWrap(title, lang, family, logins_cache, table)
    # ---
    logins_cache.update(logins_cache2)
    # ---
    page = super_page.MainPage(login_bot, title, lang, family=family)
    # ---
    return page

def CatDepth(title, sitecode="", family="wikipedia", **kwargs):
    # ---
    table = User_tables.get((sitecode, family)) or User_tables.get(("*", family))
    # ---
    login_bot, logins_cache2 = LoginWrap(title, sitecode, family, logins_cache, table)
    # ---
    logins_cache.update(logins_cache2)
    # ---
    result = catdepth_new.subcatquery(login_bot, title, sitecode=sitecode, family=family, **kwargs)
    # ---
    return result

__all__ = [
    # "bot_api",
    # "super_page",
    "catdepth_new",
    "MainPage",
    "add_Usertables",
    "CatDepth",
]
