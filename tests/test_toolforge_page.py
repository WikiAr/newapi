"""

python3 core8/pwb.py newapi/tests/test_toolforge_page nomwclient
python3 core8/pwb.py newapi/tests/test_toolforge_page nomwclient
python3 core8/pwb.py newapi/tests/test_toolforge_page

wikiapi_new:
python3 core8/pwb.py newapi/tests/test_toolforge_page wikiapi_new nomwclient
python3 core8/pwb.py newapi/tests/test_toolforge_page wikiapi_new nomwclient
python3 core8/pwb.py newapi/tests/test_toolforge_page wikiapi_new

"""
import sys

sys.argv.append("printurl")
sys.argv.append("ask")

if "wikiapi_new" in sys.argv:
    from wikiapi_new import toolforge_page
else:
    from newapi import toolforge_page

from copy_to_en.bots import medwiki_account

User_tables_md = {
    "username": medwiki_account.username,
    "password": medwiki_account.password,
}

toolforge_page.super_page.add_Usertables(User_tables_md, "toolforge")
toolforge_page.catdepth_new.add_Usertables(User_tables_md, "toolforge")
# ---
CatDepth = toolforge_page.catdepth_new.subcatquery
MainPage = toolforge_page.super_page.MainPage

# ---
page = MainPage("Main_Page", "medwiki", family="toolforge")
# ---
text = page.get_text()
print(f"{len(text)=}")
