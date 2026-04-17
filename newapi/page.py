""" """

import functools
import os
import sys

from .all_apis import ALL_APIS
from .super.S_API import bot_api

MainPage_DEPRECATION_WARNING = """
    NEW_API is deprecated. Please use:
    from api_page import load_main_api
    api = load_main_api("en", "wikipedia")
    page = api.MainPage('title')
"""

CatDepth_DEPRECATION_WARNING = """
    NEW_API is deprecated. Please use:
    from api_page import load_main_api
    api = load_main_api("en", "wikipedia")
    cat_members = api.CatDepth('Category Title', depth=0, ns=10, nslist=[], ...)
"""

NEW_API_DEPRECATION_WARNING = """
    NEW_API is deprecated. Please use:
    from api_page import load_main_api
    api = load_main_api("en", "wikipedia")
    new_api = api.NEW_API()
    result = new_api.Get_All_pages(start="!", namespace=0, ...)
"""


@functools.lru_cache(maxsize=1)
def _load_credentials() -> tuple[str, str]:
    username = os.getenv("WIKIPEDIA_BOT_USERNAME", "")
    password = os.getenv("WIKIPEDIA_BOT_PASSWORD", "")

    if "workibrahem" in sys.argv:
        username = os.getenv("WIKIPEDIA_HIMO_USERNAME", "")
        password = os.getenv("WIKIPEDIA_HIMO_PASSWORD", "")

    return username, password


@functools.lru_cache(maxsize=1)
def load_main_api(lang, family="wikipedia") -> ALL_APIS:
    """
    Loads and returns an instance of ALL_APIS for the specified language and family, using cached credentials.
    """
    username, password = _load_credentials()
    return ALL_APIS(
        lang=lang,
        family=family,
        username=username,
        password=password,
    )


@DeprecationWarning(MainPage_DEPRECATION_WARNING)
def MainPage(title, lang, family="wikipedia"):
    # ---
    main_bot = load_main_api(lang, family)
    # ---
    page = main_bot.MainPage(title, lang, family=family)
    # ---
    return page


@DeprecationWarning(CatDepth_DEPRECATION_WARNING)
def CatDepth(title, sitecode="", family="wikipedia", **kwargs):
    # ---
    main_bot = load_main_api(sitecode, family)
    # ---
    result = main_bot.CatDepth(title, sitecode=sitecode, family=family, **kwargs)
    # ---
    return result


@DeprecationWarning(NEW_API_DEPRECATION_WARNING)
def NEW_API(lang="", family="wikipedia") -> bot_api.NEW_API:
    main_bot = load_main_api(lang, family)
    return main_bot.NEW_API()


__all__ = [
    "MainPage",
    "NEW_API",
    "CatDepth",
]
