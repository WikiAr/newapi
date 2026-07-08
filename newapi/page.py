""" """

import functools
import os

from .all_apis import AllAPIS
from .config import settings
from .super.S_API import bot_api


@functools.lru_cache(maxsize=1)
def _load_credentials() -> tuple[str, str]:
    username = os.getenv("WIKIPEDIA_BOT_USERNAME", "")
    password = os.getenv("WIKIPEDIA_BOT_PASSWORD", "")

    if settings.bot.workibrahem:
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


def MainPage(title, lang, family: str = "wikipedia"):
    # ---
    main_bot = load_main_api(lang, family)
    # ---
    page = main_bot.MainPage(title, lang, family=family)
    # ---
    return page


def CatDepth(title, sitecode: str = "", family: str = "wikipedia", **kwargs):
    # ---
    main_bot = load_main_api(sitecode, family)
    # ---
    result = main_bot.CatDepth(title, sitecode=sitecode, family=family, **kwargs)
    # ---
    return result


def NewApi(lang: str = "", family: str = "wikipedia") -> bot_api.NewApi:
    main_bot = load_main_api(lang, family)
    return main_bot.NewApi()


__all__ = [
    "MainPage",
    "NewApi",
    "CatDepth",
]
