""" """

from __future__ import annotations

import logging
from typing import Any

from ..api_client import WikiLoginClient
from . import bot_api
from .categories import catdepth_new
from .pages import super_page

logger = logging.getLogger(__name__)


class AllAPIS:
    """
    A class that provides access to various API functionalities.
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

    def mainpage(self, title: str, *args, **kwargs) -> super_page.MainPage:
        return super_page.MainPage(self.login_bot, title, self.lang, family=self.family)

    def mainpagesolvereditect(self, title: str, *args, **kwargs) -> super_page.MainPage:
        page = super_page.MainPage(self.login_bot, title, self.lang, family=self.family)

        if page.isredirect():
            target = page.get_redirect_target()
            if target:
                return super_page.MainPage(self.login_bot, target, self.lang, family=self.family)

        return page

    def catdepth(
        self,
        title: str,
        **kwargs,
    ) -> dict[Any, Any]:
        return catdepth_new.subcatquery(
            self.login_bot,
            title,
            sitecode=self.lang,
            family=self.family,
            **kwargs,
        )

    def newapi(self, *args, **kwargs) -> bot_api.NewApi:
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
