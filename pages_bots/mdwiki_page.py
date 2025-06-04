# ---
"""
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
# ---
import os
import sys
# ---
home_dir = os.getenv("HOME")
# ---
if "mwclient" not in sys.argv:
    sys.argv.append("nomwclient")
    print("sys.argv.append('nomwclient')")

from ..super.S_API import bot_api
from ..super.S_Category import catdepth_new
from ..super.S_Page import super_page
from ..super.S_Login.login_wrap import LoginWrap
from ..api_utils.user_agent import default_user_agent
from ..api_utils import lang_codes

from ..accounts.user_account_new import User_tables, SITECODE, FAMILY
# ---
user_agent = default_user_agent()
# ---
bot_api.add_Usertables(User_tables, FAMILY)
# ---
NEW_API = bot_api.NEW_API
change_codes = lang_codes.change_codes
# CatDepth = catdepth_new.subcatquery

logins_cache = {}

def MainPage(title, lang, family=FAMILY):
    # ---
    login_bot, logins_cache2 = LoginWrap(title, lang, family, logins_cache, User_tables)
    # ---
    logins_cache.update(logins_cache2)
    # ---
    page = super_page.MainPage(login_bot, title, lang, family=family)
    # ---
    return page

def CatDepth(title, sitecode=SITECODE, family=FAMILY, **kwargs):
    # ---
    login_bot, logins_cache2 = LoginWrap(title, sitecode, family, logins_cache, User_tables)
    # ---
    logins_cache.update(logins_cache2)
    # ---
    result = catdepth_new.subcatquery(login_bot, title, sitecode=sitecode, family=family, **kwargs)
    # ---
    return result

md_MainPage = MainPage

__all__ = [
    'home_dir',
    'user_agent',
    'MainPage',
    'md_MainPage',
    'NEW_API',
    'CatDepth',
    'change_codes',
]
