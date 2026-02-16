# ---
"""

from newapi.ncc_page import CatDepth

# cat_members = CatDepth(title, sitecode='www', family="nccommons", depth=0, ns=10, nslist=[], onlyns=False, tempyes=[])

from newapi.ncc_page import MainPage as ncc_MainPage
'''
page      = ncc_MainPage(title, 'www', family='nccommons')
exists    = page.exists()
if not exists: return
# ---
'''


from newapi.ncc_page import NEW_API
# api_new  = NEW_API('www', family='nccommons')
# login    = api_new.Login_to_wiki()
# json1    = api_new.post_params(params, addtoken=False)
# pages    = api_new.Find_pages_exists_or_not(liste)
# pages    = api_new.Get_All_pages(start='', namespace="0", limit="max", apfilterredir='', limit_all=0)
# search   = api_new.Search(value='', ns="", offset='', srlimit="max", RETURN_dict=False, addparams={})
# newpages = api_new.Get_Newpages(limit="max", namespace="0", rcstart="", user='')
# usercont = api_new.UserContribs(user, limit=5000, namespace="*", ucshow="")
# l_links  = api_new.Get_langlinks_for_list(titles, targtsitecode="", numbes=50)
# text_w   = api_new.expandtemplates(text)
# subst    = api_new.Parse_Text('{{subst:page_name}}', title)
# revisions= api_new.get_revisions(title)

"""

import os

# import sys
# ---
home_dir = os.getenv("HOME")
from ..accounts.user_account_ncc import FAMILY, SITECODE, User_tables
from ..api_utils import lang_codes
from ..api_utils.user_agent import default_user_agent
from ..super.login_wrap import LoginWrap

# ---
from ..super.S_API import bot_api
from ..super.S_Category import catdepth_new
from ..super.S_Page import super_page

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


def MainPage(title, lang, family=FAMILY):
    # ---
    login_bot = log_it(lang, family)
    # ---
    page = super_page.MainPage(login_bot, title, lang, family=family)
    # ---
    return page


def CatDepth(title, sitecode=SITECODE, family=FAMILY, **kwargs):
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


ncc_MainPage = MainPage

__all__ = [
    "home_dir",
    "user_agent",
    "MainPage",
    "ncc_MainPage",
    "NEW_API",
    "CatDepth",
    "change_codes",
]
