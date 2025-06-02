"""
from newapi import toolforge_page
# ---
User_tables_md = {
    "username": medwiki_account.username,
    "password": medwiki_account.password,
}
# ---
toolforge_page.super_page.add_Usertables(User_tables_md, "toolforge")
toolforge_page.catdepth_new.add_Usertables(User_tables_md, "toolforge")
# ---
CatDepth = toolforge_page.catdepth_new.subcatquery
MainPage = toolforge_page.super_page.MainPage
# ---
"""
# ---
from ..super.S_API import bot_api
from ..super.S_Page import super_page
from ..super.S_Category import catdepth_new

__all__ = [
    "bot_api",
    "super_page",
    "catdepth_new",
]
