# ---
"""
from newapi.ncc_page import CatDepth, CatDepthLogin
# CatDepthLogin(sitecode="www", family="nccommons")
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
import sys
import os
import configparser
from pathlib import Path
from ..super.S_API import bot_api
from ..super.S_Page import super_page
from ..super.S_Category import catdepth_new

print_test = {1: True if "test" in sys.argv else False}

def printt(s):
    if print_test[1]:
        print(s)


catdepth_new.SITECODE = "www"
catdepth_new.FAMILY = "nccommons"


dir2 = os.getenv("HOME")
printt(f"HOME:{dir2}")
# ---
if not dir2:
    Dir = str(Path(__file__).parents[0])
    # ---
    dir2 = Dir.replace("\\", "/")
    dir2 = dir2.split("/nccbot/")[0]
    # ---
    if dir2.startswith("I:"):
        dir2 = "I:/ncc"
# ---
file_path = Path(dir2) / "confs" / "nccommons_user.ini"
# ---
printt(f"{file_path=}")

if not file_path.exists():
    print(f"File not found: {file_path}")
# ---
config = configparser.ConfigParser()
config.read(f"{dir2}/confs/nccommons_user.ini")
# ---
username = config["DEFAULT"].get("username", "").strip()
password = config["DEFAULT"].get("password", "").strip()
# ---
printt(f"{username=}")
# ---
User_tables = {
    "username": username,
    "password": password,
}
# ---
user_agent = super_page.default_user_agent()
# ---
super_page.add_Usertables(User_tables, "nccommons")
bot_api.add_Usertables(User_tables, "nccommons")
catdepth_new.add_Usertables(User_tables, "nccommons")
# ---
NEW_API = bot_api.NEW_API
# ---
MainPage = super_page.MainPage
ncc_MainPage = super_page.MainPage
# ---
change_codes = super_page.change_codes
CategoryDepth = catdepth_new.CategoryDepth
CatDepth = catdepth_new.subcatquery
CatDepthLogin = catdepth_new.login_wiki
# ---
# xxxxxxxxxxx
home_dir = os.getenv("HOME")

__all__ = [
    'home_dir',
    'user_agent',
    'ncc_MainPage',
    'MainPage',
    'NEW_API',
    'CatDepth',
    'CatDepthLogin',
    'CategoryDepth',
    'change_codes',
]
