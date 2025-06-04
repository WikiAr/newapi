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
from ..super.S_Page.page_wrap import MainPageWrap
from ..super.S_Category import catdepth_new

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
    table = User_tables.get((lang, family)) or User_tables.get(("*", family))
    # ---
    page, cat_bots_login2 = MainPageWrap(title, lang, family, cat_bots_login, {family: table})
    cat_bots_login.update(cat_bots_login2)
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
