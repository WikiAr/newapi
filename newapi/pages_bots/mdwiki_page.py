# ---
"""
"""
# ---
import os
import functools
import sys

if "mwclient" not in sys.argv:
    sys.argv.append("nomwclient")

from .all_apis import ALL_APIS
from ..api_utils.user_agent import default_user_agent
from ..api_utils import lang_codes
from ..accounts.user_account_new import User_tables

user_agent = default_user_agent()

change_codes = lang_codes.change_codes

home_dir = os.getenv("HOME")


@functools.lru_cache(maxsize=1)
def load_main_api() -> ALL_APIS:
    return ALL_APIS(
        lang="www",
        family="mdwiki",
        username=User_tables["username"],
        password=User_tables["password"],
    )


main_api = load_main_api()
NEW_API = main_api.NEW_API
MainPage = main_api.MainPage
CatDepth = main_api.CatDepth
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
