"""
Test runner usage: python3 core8/pwb.py newapi_bot/z_te_sts/test_runner
"""

import sys

# sys.argv.append("printurl")
sys.argv.append("ask")

from newapi.mdwiki_page import CatDepth, MainPage

"""
text      = page.get_text()
timestamp = page.get_timestamp()
user      = page.get_user()
links     = page.page_links()
words     = page.get_words()
purge     = page.purge()
templates = page.get_templates()
save_page = page.save(newtext='', summary='', nocreate=1, minor='')
create    = page.Create(text='', summary='')
"""
# ---
"""
page = MainPage("Category:RTT", "www", family="mdwiki")
# ---
text = page.get_text()
print(f"{len(text)=}")

# ---
# ex = page.page_backlinks()
# print('---------------------------')
# print(f'page_backlinks:{ex}')

page_backlinks = page.page_backlinks()
print("---------------------------")
print(f"{len(page_backlinks)=}")

red = page.page_links()
print(f"{len(red)=}")
# ---
"""
# ---
# hidden_categories= page.get_hidden_categories()
# print('---------------------------')
# print(f'hidden_categories:{hidden_categories}')
# ---


def test_main_page():
    page = MainPage("Category:RTT", "www", family="mdwiki")
    # ---
    text = page.get_text()
    print(f"MainPage RTT: {len(text)=}")
    assert len(text) > 0


def test_main_page2():
    page = MainPage("Main_Page", "www", family="mdwiki")
    exists = page.exists()
    assert exists is True


def test_cat_members():
    cat_members = CatDepth("RTT", sitecode="www", family="mdwiki", depth=3, ns="0")
    # ---
    print(f"RTT: {len(cat_members)=}")
    assert len(cat_members) > 0


def test_cat_members2():
    cat_members = CatDepth("RTTNEURO", sitecode="www", family="mdwiki", depth=3, ns="0")
    # ---
    print(f"RTTNEURO: {len(cat_members)=}")
    assert len(cat_members) > 0


# ---
# save = page.save(newtext='')
# api_new = NEW_API('en', family='mdwiki')
# login   = api_new.Login_to_wiki()
# pages   = api_new.Find_pages_exists_or_not(liste)
# pages   = api_new.Get_Newpages()
