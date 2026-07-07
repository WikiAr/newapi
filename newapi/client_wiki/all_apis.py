""" """

import logging

from ..api_client import WikiLoginClient
from ..super.S_API import bot_api
from .categories import catdepth_new
from .pages import super_page

logger = logging.getLogger(__name__)


class AllAPIS:
    """
    A class that provides access to various API functionalities.
    Usage:
        from newapi import AllAPIS
        main_api = AllAPIS(lang='en', family='wikipedia', username='your_username', password='your_password')
        page = main_api.MainPage('Main Page Title')
        cat_members = main_api.CatDepth('Category Title')
        new_api = main_api.NewApi()
    """

    def __init__(
        self,
        lang: str,
        family: str,
        username: str,
        password: str,
        use_cookies: bool = True,
        cookies_dir: None | str = None,
    ) -> None:
        self.lang = lang
        self.family = family
        self.username = username
        self.password = password
        self.use_cookies = use_cookies
        self.cookies_dir = cookies_dir
        self.login_bot = self._login()

    def MainPage(self, title: str, *args, **kwargs) -> super_page.MainPage:
        return super_page.MainPage(self.login_bot, title, self.lang, family=self.family)

    def CatDepth(self, title: str, sitecode: str = "", family: str = "", *args, **kwargs):
        return catdepth_new.subcatquery(self.login_bot, title, sitecode=self.lang, family=self.family, **kwargs)

    def NewApi(self, *args, **kwargs) -> bot_api.NewApi:
        # ---
        return bot_api.NewApi(self.login_bot, lang=self.lang, family=self.family)

    def _login(self) -> WikiLoginClient:
        client = WikiLoginClient(
            lang=self.lang,
            family=self.family,
            username=self.username,
            password=self.password,
            use_cookies=self.use_cookies,
            cookies_dir=self.cookies_dir,
        )
        return client


__all__ = [
    "AllAPIS",
]
