"""
Test runner usage: python3 core8/pwb.py newapi_bot/z_te_sts/test_runner
"""
import sys

sys.argv.append("printurl")
sys.argv.append("ask")

from newapi.page import MainPage, CatDepth

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
page = MainPage("تصنيف:اليمن", "ar", family="wikipedia")
# ---
text = page.get_text()
print(f"{len(text)=}")

# ---
# ex = page.page_backlinks()
# print('---------------------------')
# print(f'page_backlinks:{ex}')
page2 = MainPage("Category:Yemen", "en", family="wikipedia")
# ---
text2 = page2.get_text()
print(f"{len(text2)=}")
# ---
page_backlinks = page.page_backlinks()
print("---------------------------")
print(f"{len(page_backlinks)=}")

# ---
# ---
# hidden_categories= page.get_hidden_categories()
# print('---------------------------')
# print(f'hidden_categories:{hidden_categories}')
# ---
cat_members = CatDepth("Association football players by nationality", sitecode="en", family="wikipedia", depth=0, ns="14")
# ---
print(f"{len(cat_members)=}")
# ---
red = page.page_links()
print(f"{len(red)=}")
# ---
# save = page.save(newtext='')
# api_new = NEW_API('en', family='wikipedia')
# login   = api_new.Login_to_wiki()
# pages   = api_new.Find_pages_exists_or_not(liste)
# pages   = api_new.Get_Newpages()


# python3 core8/pwb.py newapi/wiki_page
