""" """

import functools
import os

from .all_apis import AllAPIS
from .client_wiki import bot_api
from .config import main_settings


@functools.lru_cache(maxsize=1)
def _load_credentials() -> tuple[str, str]:
    username = os.getenv("WIKIPEDIA_BOT_USERNAME", "")
    password = os.getenv("WIKIPEDIA_BOT_PASSWORD", "")

    if main_settings.bot.workibrahem:
        username = os.getenv("WIKIPEDIA_HIMO_USERNAME", "")
        password = os.getenv("WIKIPEDIA_HIMO_PASSWORD", "")

    return username, password


@functools.lru_cache(maxsize=1)
def load_main_api(lang, family: str = "wikipedia") -> AllAPIS:
    """
    Loads and returns an instance of AllAPIS for the specified language and family, using cached credentials.
    """
    username, password = _load_credentials()
    return AllAPIS(
        lang=lang,
        family=family,
        username=username,
        password=password,
    )


def mainpage(title, lang, family: str = "wikipedia"):
    # ---
    main_bot = load_main_api(lang, family)
    # ---
    page = main_bot.mainpage(title, lang, family=family)
    # ---
    return page


def catdepth(title, sitecode: str = "", family: str = "wikipedia", **kwargs):
    # ---
    main_bot = load_main_api(sitecode, family)
    # ---
    result = main_bot.catdepth(title, sitecode=sitecode, family=family, **kwargs)
    # ---
    return result


def newapi(lang: str = "", family: str = "wikipedia") -> bot_api.NewApi:
    main_bot = load_main_api(lang, family)
    return main_bot.newapi()


__all__ = [
    "mainpage",
    "newapi",
    "catdepth",
]
