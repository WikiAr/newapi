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
from ..super.S_Page import super_page
from ..super.S_Login.super_login import Login
from ..super.S_Page.page_wrap import MainPageWrap
from ..super.S_Category import catdepth_new
from ..api_utils import printe

User_tables = {}

def add_Usertables(table, family, lang):
    # ---
    User_tables[(lang, family)] = table
    User_tables[("*", family)] = table
    # ---
    catdepth_new.add_Usertables(table, family)

cat_bots_login = {}

def MainPage(title, lang, family="wikipedia"):
    # ---
    page, cat_bots_login2 = MainPageWrap(title, lang, family, cat_bots_login, User_tables_x)
    cat_bots_login.update(cat_bots_login2)
    # ---
    return page

def MainPage(title, lang, family="toolforge"):
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
        table = User_tables.get(cache_key) or User_tables.get(("*", family))
        # ---
        login_bot.add_users(table, lang=lang)
        # ---
        cat_bots_login[cache_key] = login_bot
    # ---
    page = super_page.MainPage(login_bot, title, lang, family=family)
    # ---
    return page

CatDepth = catdepth_new.subcatquery

__all__ = [
    # "bot_api",
    # "super_page",
    "catdepth_new",
    "MainPage",
    "add_Usertables",
    "CatDepth",
]
