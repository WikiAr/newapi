"""

"""
# ---
import functools
import os
import sys
from ..super.S_API import bot_api
from ..api_utils.user_agent import default_user_agent
from ..api_utils import lang_codes
from .all_apis import ALL_APIS

from ..accounts.useraccount import User_tables_bot, User_tables_ibrahem
home_dir = os.getenv("HOME")
# ---
User_tables = User_tables_bot
# ---
if "workibrahem" in sys.argv:
    User_tables = User_tables_ibrahem
    # ---
    print(f"page.py use {User_tables['username']} account.")

user_agent = default_user_agent()
change_codes = lang_codes.change_codes
logins_cache = {}


@functools.lru_cache(maxsize=1)
def load_main_api(lang, family) -> ALL_APIS:
    return ALL_APIS(
        lang=lang,
        family=family,
        username=User_tables["username"],
        password=User_tables["password"],
    )


def MainPage(title, lang, family="wikipedia"):
    # ---
    main_bot = load_main_api(lang, family)
    # ---
    page = main_bot.MainPage(title, lang, family=family)
    # ---
    return page


def CatDepth(title, sitecode="", family="wikipedia", **kwargs):
    # ---
    main_bot = load_main_api(sitecode, family)
    # ---
    result = main_bot.CatDepth(title, sitecode=sitecode, family=family, **kwargs)
    # ---
    return result


def NEW_API(lang="", family="wikipedia") -> bot_api.NEW_API:
    main_bot = load_main_api(lang, family)
    return main_bot.NEW_API()


__all__ = [
    'home_dir',
    'user_agent',
    'MainPage',
    'NEW_API',
    'CatDepth',
    'change_codes',
]
