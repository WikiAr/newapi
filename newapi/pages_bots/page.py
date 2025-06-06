"""
from newapi.page import MainPage, NEW_API, CatDepth

Usage:

from newapi.page import CatDepth

# cat_members = CatDepth(title, sitecode='en', family="wikipedia", depth=0, ns="all", nslist=[], without_lang="", with_lang="", tempyes=[])

from newapi.page import MainPage, NEW_API
# api_new = NEW_API('en', family='wikipedia')
# json1    = api_new.post_params(params, addtoken=False)
# move_it  = api_new.move(old_title, to, reason="", noredirect=False, movesubpages=False)
# pages    = api_new.Find_pages_exists_or_not(liste, get_redirect=False)
# pages    = api_new.Get_All_pages(start='', namespace="0", limit="max", apfilterredir='', limit_all=0)
# search   = api_new.Search(value='', ns="", offset='', srlimit="max", RETURN_dict=False, addparams={})
# newpages = api_new.Get_Newpages(limit="max", namespace="0", rcstart="", user='')
# usercont = api_new.UserContribs(user, limit=5000, namespace="*", ucshow="")
# l_links  = api_new.Get_langlinks_for_list(titles, targtsitecode="", numbes=50)
# text_w   = api_new.expandtemplates(text)
# subst    = api_new.Parse_Text('{{subst:page_name}}', title)
# extlinks = api_new.get_extlinks(title)
# revisions= api_new.get_revisions(title)
# logs     = api_new.get_logs(title)
# wantedcats  = api_new.querypage_list(qppage='Wantedcategories', qplimit="max", Max=5000)
# pages  = api_new.Get_template_pages(title, namespace="*", Max=10000)
"""
# ---
import os
import sys
from ..super.S_API import bot_api
from ..super.S_Category import catdepth_new

from ..super.S_Page import super_page
from ..super.S_Login.login_wrap import LoginWrap
from ..api_utils.user_agent import default_user_agent
from ..api_utils import lang_codes

from ..accounts.useraccount import User_tables_bot, User_tables_ibrahem
home_dir = os.getenv("HOME")
# ---
User_tables = User_tables_bot
# ---
if "workibrahem" in sys.argv:
    User_tables = User_tables_ibrahem
    # ---
    print(f"page.py use {User_tables['username']} account.")
# ---
user_agent = default_user_agent()
# ---
change_codes = lang_codes.change_codes

logins_cache = {}

def log_it(lang, family):
    # ---
    login_bot, logins_cache2 = LoginWrap(lang, family, logins_cache, User_tables)
    # ---
    logins_cache.update(logins_cache2)
    # ---
    return login_bot

def MainPage(title, lang, family="wikipedia"):
    # ---
    login_bot = log_it(lang, family)
    # ---
    page = super_page.MainPage(login_bot, title, lang, family=family)
    # ---
    return page

def CatDepth(title, sitecode="", family="wikipedia", **kwargs):
    # ---
    login_bot = log_it(sitecode, family)
    # ---
    result = catdepth_new.subcatquery(login_bot, title, sitecode=sitecode, family=family, **kwargs)
    # ---
    return result

def NEW_API(lang="", family="wikipedia"):
    # ---
    login_bot = log_it(lang, family)
    # ---
    result = bot_api.NEW_API(login_bot, lang=lang, family=family)
    # ---
    return result

__all__ = [
    'home_dir',
    'user_agent',
    'MainPage',
    'NEW_API',
    'CatDepth',
    'change_codes',
]
