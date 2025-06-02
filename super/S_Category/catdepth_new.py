"""

from newapi.ncc_page import CatDepth
# cat_members = CatDepth(title, sitecode='www', family="nccommons", depth=0, ns=10, nslist=[], onlyns=False, tempyes=[])

"""
import time
import sys

from ...api_utils import printe
from .bot import CategoryDepth, add_Usertables as su_add_Usertables

SITECODE = "en"
FAMILY = "wikipedia"

def add_Usertables(table, family):
    return su_add_Usertables(table, family)

cat_bots_login = {}

def subcatquery(title, sitecode=SITECODE, family=FAMILY, **kwargs):
    # ---
    print_s = kwargs.get("print_s", True)
    # ---
    priffixs = {"ar": "تصنيف:", "en": "Category:", "www": "Category:"}
    # ---
    start_priffix = priffixs.get(sitecode)
    # ---
    if start_priffix and not title.startswith(start_priffix):
        title = start_priffix + title
    # ---
    args2 = {
        "title": title,
        "depth": None,
        "ns": None,
        "nslist": None,
        "onlyns": None,
        "without_lang": None,
        "with_lang": None,
        "tempyes": None,
        "props": None,
        "only_titles": None
    }
    # ---
    if print_s:
        printe.output(f"<<lightyellow>> catdepth_new.py sub cat query for {sitecode}:{title}, depth:{args2['depth']}, ns:{args2['ns']}, onlyns:{args2['onlyns']}")
    # ---
    start = time.time()
    final = time.time()
    # ---
    for k, v in kwargs.items():
        if k not in args2 or args2[k] is None:
            args2[k] = v
    # ---
    if cat_bots_login.get(sitecode + family):
        bot = cat_bots_login[sitecode + family]
    else:
        bot = CategoryDepth(title, sitecode=sitecode, family=family, **kwargs)
        # ---
        cat_bots_login[sitecode + family] = bot
    # ---
    result = bot.subcatquery_(**args2)
    # ---
    get_revids = kwargs.get("get_revids", False)
    # ---
    if get_revids:
        result = bot.get_revids()
    # ---
    final = time.time()
    delta = int(final - start)
    # ---
    if "printresult" in sys.argv:
        printe.output(result)
    # ---
    lenpages = bot.get_len_pages()
    # ---
    if print_s:
        printe.output(f"<<lightblue>>catdepth_new.py: find {len(result)} pages({args2['ns']}) in {sitecode}:{title}, depth:{args2['depth']} in {delta} seconds | {lenpages=}")
    # ---
    return result
