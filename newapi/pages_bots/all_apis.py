"""

main_api = ALL_APIS(lang='en', family='wikipedia', username='your_username', password='your_password')
page = main_api.MainPage('Main Page Title')
cat_members = main_api.CatDepth('Category Title')
new_api = main_api.NEW_API()
"""

import functools
import logging

from ..api_client.client import WikiLoginClient
from ..super.S_API import bot_api
from ..super.S_Category import catdepth_new
from ..super.S_Page import super_page

logger = logging.getLogger(__name__)


class ALL_APIS:  # noqa: N801
    """
    A class that provides access to various API functionalities.
    Usage:
        from newapi import ALL_APIS
        main_api = ALL_APIS(lang='en', family='wikipedia', username='your_username', password='your_password')
        page = main_api.MainPage('Main Page Title')
        cat_members = main_api.CatDepth('Category Title')
        new_api = main_api.NEW_API()
    """

    def __init__(self, lang: str, family: str, username: str, password: str) -> None:
        self.lang = lang
        self.family = family
        self.username = username
        self.password = password
        self.login_bot = self._login()

    def MainPage(self, title, *args, **kwargs) -> super_page.MainPage:
        return super_page.MainPage(self.login_bot, title, self.lang, family=self.family)

    def CatDepth(self, title, sitecode="", family="", *args, **kwargs):
        # cat_members = CatDepth("RTTNEURO", sitecode="www", family="mdwiki", depth=3, ns="0")
        return catdepth_new.subcatquery(self.login_bot, title, sitecode=self.lang, family=self.family, **kwargs)

    def NEW_API(self, *args, **kwargs) -> bot_api.NEW_API:
        # ---
        return bot_api.NEW_API(self.login_bot, lang=self.lang, family=self.family)

    def _login(self) -> WikiLoginClient:
        return WikiLoginClient(
            lang=self.lang,
            family=self.family,
            username=self.username,
            password=self.password,
        )


__all__ = [
    "ALL_APIS",
]
