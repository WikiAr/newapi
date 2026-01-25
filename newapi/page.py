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
from .pages_bots.page import (
    home_dir,
    MainPage,
    user_agent,
    NEW_API,
    CatDepth,
    change_codes,
)

__all__ = [
    "home_dir",
    "user_agent",
    "MainPage",
    "NEW_API",
    "CatDepth",
    "change_codes",
]
