"""

python3 core8/pwb.py newapi/tests/test_mdwiki_page nomwclient
python3 core8/pwb.py newapi/tests/test_mdwiki_page nomwclient
python3 core8/pwb.py newapi/tests/test_mdwiki_page

wikiapi_new:
python3 core8/pwb.py newapi/tests/test_mdwiki_page wikiapi_new nomwclient
python3 core8/pwb.py newapi/tests/test_mdwiki_page wikiapi_new nomwclient
python3 core8/pwb.py newapi/tests/test_mdwiki_page wikiapi_new
"""
import sys

sys.argv.append("printurl")
sys.argv.append("ask")

if "wikiapi_new" in sys.argv:
    from wikiapi_new.mdwiki_page import MainPage, CatDepth
else:
    from newapi.mdwiki_page import MainPage, CatDepth

"""
page      = MainPage(title, 'ar', family='wikipedia')
exists    = page.exists()
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

# ---
# hidden_categories= page.get_hidden_categories()
# print('---------------------------')
# print(f'hidden_categories:{hidden_categories}')
# ---
cat_members = CatDepth("RTT", sitecode="www", family="mdwiki", depth=0, ns="14")
# ---
print(f"{len(cat_members)=}")
# ---
red = page.page_links()
print(f"{len(red)=}")
# ---
# save = page.save(newtext='')
# api_new = NEW_API('en', family='mdwiki')
# login   = api_new.Login_to_wiki()
# pages   = api_new.Find_pages_exists_or_not(liste)
# pages   = api_new.Get_Newpages()
