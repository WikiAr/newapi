"""

python3 core8/pwb.py newapi/tests/test_page printurl nomwclient
python3 core8/pwb.py newapi/tests/test_page printurl

"""
import sys
# sys.argv.append("printurl")
sys.argv.append("ask")
from newapi.page import MainPage

page = MainPage("وبxx:ملعب", "ar")
print(page.exists())

pageen = MainPage("الصفحة الرxئيسة", 'ar')
print(pageen.exists())


# ---
page = MainPage("وب:ملعب", "ar")
pageen = MainPage("User:Mr. Ibrahem/sandbox", 'simple')
# ---
existsen = pageen.exists()

if not page.can_edit():
    print("page can't edit!")
# ---
"""
if page.isRedirect() :	return
# target = page.get_redirect_target()
# ---
text	    = page.get_text()
ns		    = page.namespace()
links	    = page.page_links()
categories  = page.get_categories(with_hidden=False)
langlinks   = page.get_langlinks()
back_links  = page.page_backlinks()
wiki_links  = page.get_wiki_links_from_text()
words	    = page.get_words()
templates   = page.get_templates()
save_page   = page.save(newtext='', summary='', nocreate=1, minor='')
create	    = page.Create(text='', summary='')
# ---
text_html   = page.get_text_html()
hidden_categories= page.get_hidden_categories()
flagged     = page.is_flagged()
timestamp   = page.get_timestamp()
user	    = page.get_user()
purge	    = page.purge()
"""

# ---
text = page.get_text()
print("---------------------------")
print(f"text:{len(text)=}")
# ---
ex = page.get_wiki_links_from_text()
print("---------------------------")
print(f"get_wiki_links_from_text:{len(ex)=}")
# ---
hidden_categories = page.get_hidden_categories()
print("---------------------------")
print(f"hidden_categories:{len(hidden_categories)=}")
# ---
backlinks = page.page_backlinks()
print("---------------------------")
print(f"backlinks:{len(backlinks)=}")
# ---

newtext = "تجربة!\n" * 6
# ---
save = page.save(newtext=newtext)


pageen.save(newtext="!!!", nocreate=0)


save = page.save(newtext="!")

