"""
Test runner usage: python3 core8/pwb.py newapi_bot/z_te_sts/test_runner
"""

import sys

sys.path.append("I:/mdwiki/pybot")
sys.argv.append("ask")
from copy_to_en.bots import medwiki_account
from newapi import toolforge_page

User_tables_md = {
    "username": medwiki_account.username,
    "password": medwiki_account.password,
}
# ---
User_tables_mdcx = {
    "username": medwiki_account.username_cx,
    "password": medwiki_account.password_cx,
}
# ---
toolforge_page.add_User_table(User_tables_md, "toolforge", "medwiki")
# ---
toolforge_page.add_User_table(User_tables_mdcx, "toolforge", "mdwikicx")
# ---
CatDepth = toolforge_page.CatDepth
MainPage = toolforge_page.MainPage

lists = {"page": "Main_Page", "cat": "Category:Translations"}
# ---
for site in ["medwiki", "mdwikicx"]:
    # ---
    print(f"___________________{site=}___________________")
    # ---
    print("//////// page ////////")
    # ---
    title = "Main_Page"
    Category = "Category:Translations"
    # ---
    print(f"{site=}, {title=}")
    # ---
    page = MainPage(title, site, family="toolforge")
    # ---
    text = page.get_text()
    print(f"{len(text)=}")
    # ---
    print("//////// Category ////////")
    # ---
    members = CatDepth(Category, sitecode=site, family="toolforge", ns=14)
    # ---
    print(members.keys())
    print(f"{site=} {Category=}, members: {len(members)}")
