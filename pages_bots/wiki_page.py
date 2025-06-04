"""
Usage:

from newapi.wiki_page import CatDepth

# cat_members = CatDepth(title, sitecode='en', family="wikipedia", depth=0, ns="all", nslist=[], without_lang="", with_lang="", tempyes=[])

from newapi.wiki_page import MainPage, NEW_API
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
from ..super.S_API import bot_api
from ..super.S_Category import catdepth_new
from ..accounts import user_account_new as useraccount

from ..super.S_Page import super_page
from ..super.S_Page.page_wrap import MainPageWrap
from ..super.S_Login.super_login import Login
from ..api_utils import printe

home_dir = os.getenv("HOME")
tool = home_dir.split("/")[-1] if home_dir else None
# ---
pyy_file = __file__.replace("\\", "/").split("/")[-1]
# ---
# User_tables = {
#     "username": useraccount.my_username,
#     "password": useraccount.my_password,
# }
# ---
# if "botuser" in sys.argv:
User_tables = {
    "username": useraccount.bot_username,
    "password": useraccount.bot_password,
}
# ---
print(f"{pyy_file} use {User_tables['username']} account.")
# ---
user_agent = super_page.default_user_agent()
# ---
bot_api.add_Usertables(User_tables, "wikipedia")
catdepth_new.add_Usertables(User_tables, "wikipedia")
# ---
bot_api.add_Usertables(User_tables, "wikidata")
catdepth_new.add_Usertables(User_tables, "wikidata")
# ---
# super_page.add_Usertables(User_tables, "wikipedia")
# super_page.add_Usertables(User_tables, "wikidata")
# ---
NEW_API = bot_api.NEW_API
change_codes = super_page.change_codes
CatDepth = catdepth_new.subcatquery

cat_bots_login = {}

def MainPage(title, lang, family="wikipedia"):
    # ---
    page, cat_bots_login2 = MainPageWrap(title, lang, family, cat_bots_login, User_tables)
    cat_bots_login.update(cat_bots_login2)
    # ---
    return page

__all__ = [
    'home_dir',
    'user_agent',
    'MainPage',
    'NEW_API',
    'CatDepth',
    'change_codes',
]
