"""
from newapi.all_apis import ALL_APIS

from newapi import ALL_APIS

main_api = ALL_APIS(lang='en', family='wikipedia', username='your_username', password='your_password')
page = main_api.MainPage('Main Page Title')
cat_members = main_api.CatDepth('Category Title')
new_api = main_api.NEW_API()
"""
# ---
import functools
from typing import Any
from ..super.S_API import bot_api
from ..super.S_Category import catdepth_new
from ..super.S_Page import super_page
from ..api_utils import printe
from ..super.super_login import Login


class ALL_APIS:
    """
    A class that provides access to various API functionalities.
    Usage:
        from newapi import ALL_APIS
        main_api = ALL_APIS(lang='en', family='wikipedia', username='your_username', password='your_password')
        page = main_api.MainPage('Main Page Title')
        cat_members = main_api.CatDepth('Category Title')
        new_api = main_api.NEW_API()
    """

    def __init__(self, lang, family, username, password) -> None:
        self.lang = lang
        self.family = family
        self.username = username
        self.password = password
        self.login_bot = self._login()

    def MainPage(self, title, *args, **kwargs) -> super_page.MainPage:
        return super_page.MainPage(self.login_bot, title, self.lang, family=self.family)

    def CatDepth(self, title, *args, **kwargs):
        return catdepth_new.subcatquery(self.login_bot, title, sitecode=self.lang, family=self.family, **kwargs)

    def NEW_API(self, *args, **kwargs):
        # ---
        return bot_api.NEW_API(self.login_bot, lang=self.lang, family=self.family)

    @functools.lru_cache(maxsize=1)
    def _login(self) -> Login[Any]:
        # ---
        login_bot = Login(self.lang, family=self.family)
        # ---
        printe.output(f"### <<purple>> LoginWrap make new bot for ({self.lang}.{self.family}.org|{self.username})", p=True)
        # ---
        user_tables = {
            self.family: {
                'username': self.username,
                'password': self.password,
            }
        }
        # ---
        login_bot.add_users(user_tables, lang=self.lang)
        # ---
        return login_bot


__all__ = [
    'ALL_APIS',
]
