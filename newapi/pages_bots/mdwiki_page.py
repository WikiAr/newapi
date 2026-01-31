# ---
"""
from newapi.mdwiki_page import load_main_api
main_api = load_main_api("www", "mdwiki")

NEW_API = main_api.NEW_API
MainPage = main_api.MainPage
CatDepth = main_api.CatDepth

from newapi.mdwiki_page import MainPage as md_MainPage, CatDepth

# cat_members = CatDepth(title, sitecode='en', family="wikipedia", depth=0, ns="all", nslist=[], onlyns=False, without_lang="", with_lang="", tempyes=[])

# from newapi.mdwiki_page import MainPage as md_MainPage
'''
page      = md_MainPage(title, 'www', family='mdwiki')
exists    = page.exists()
if not exists: return
# ---
page_edit = page.can_edit()
if not page_edit: return
# ---
if page.isRedirect() :  return
# target = page.get_redirect_target()
# ---
text        = page.get_text()
ns          = page.namespace()
links       = page.page_links()
categories  = page.get_categories(with_hidden=False)
langlinks   = page.get_langlinks()
wiki_links  = page.get_wiki_links_from_text()
refs        = page.Get_tags(tag='ref')# for x in ref: name, contents = x.name, x.contents
words       = page.get_words()
templates   = page.get_templates()
save_page   = page.save(newtext='', summary='', nocreate=1, minor='')
create      = page.Create(text='', summary='')
# ---
back_links  = page.page_backlinks()
text_html   = page.get_text_html()
hidden_categories= page.get_hidden_categories()
flagged     = page.is_flagged()
timestamp   = page.get_timestamp()
user        = page.get_user()
purge       = page.purge()
'''
"""

import functools

# ---
import os
import sys

if "mwclient" not in sys.argv:
    sys.argv.append("nomwclient")

from ..accounts.user_account_new import User_tables
from ..api_utils import lang_codes
from ..api_utils.user_agent import default_user_agent
from .all_apis import ALL_APIS

user_agent = default_user_agent()

change_codes = lang_codes.change_codes

home_dir = os.getenv("HOME")


@functools.lru_cache(maxsize=1)
def load_main_api() -> ALL_APIS:
    return ALL_APIS(
        lang="www",
        family="mdwiki",
        username=User_tables["username"],
        password=User_tables["password"],
    )


main_api = load_main_api()

NEW_API = main_api.NEW_API
MainPage = main_api.MainPage
CatDepth = main_api.CatDepth
md_MainPage = MainPage

__all__ = [
    "home_dir",
    "user_agent",
    "MainPage",
    "md_MainPage",
    "NEW_API",
    "CatDepth",
    "change_codes",
]
