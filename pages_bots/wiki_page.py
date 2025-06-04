"""
Usage:

from newapi.wiki_page import CatDepth

# cat_members = CatDepth(title, sitecode='en', family="wikipedia", depth=0, ns="all", nslist=[], without_lang="", with_lang="", tempyes=[])

from newapi.wiki_page import MainPage, NEW_API
# api_new = NEW_API('en', family='wikipedia')
# login    = api_new.Login_to_wiki()
# move_it  = api_new.move(old_title, to, reason="", noredirect=False, movesubpages=False)
# pages    = api_new.Find_pages_exists_or_not(liste, get_redirect=False)
# json1    = api_new.post_params(params, addtoken=False)
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

from ..super.S_API import bot_api as bot_api1
from ..super.S_Page import super_page as super_page1
from ..super.S_Category import catdepth_new as catdepth_new1
from ..accounts import user_account_new
from ..api_utils.user_agent import default_user_agent
# ---
home_dir = os.getenv("HOME")
# ---
User_tables = {
    "username": user_account_new.bot_username,
    "password": user_account_new.bot_password,
}
# ---
print(f"wiki_page.py use {User_tables['username']} account.")
# ---
user_agent = default_user_agent()
# ---
super_page1.add_Usertables(User_tables, "wikipedia")
bot_api1.add_Usertables(User_tables, "wikipedia")
catdepth_new1.add_Usertables(User_tables, "wikipedia")
# ---
super_page1.add_Usertables(User_tables, "wikidata")
bot_api1.add_Usertables(User_tables, "wikidata")
catdepth_new1.add_Usertables(User_tables, "wikidata")
# ---
NEW_API = bot_api1.NEW_API
MainPage = super_page1.MainPage
change_codes = super_page1.change_codes
CatDepth = catdepth_new1.subcatquery

__all__ = [
    'home_dir',
    'user_agent',
    'MainPage',
    'NEW_API',
    'CatDepth',
    'change_codes',
]
