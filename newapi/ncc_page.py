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
from .pages_bots.ncc_page import (
    home_dir,
    ncc_MainPage,
    MainPage,
    user_agent,
    NEW_API,
    CatDepth,
    change_codes
)

__all__ = [
    "home_dir",
    "user_agent",
    "ncc_MainPage",
    "MainPage",
    "NEW_API",
    "CatDepth",
    "change_codes",
]
