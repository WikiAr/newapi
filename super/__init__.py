# -*- coding: utf-8 -*-
"""
from wikiapi_new.super import super_page, catdepth_new
from wikiapi_new.super import super_page, catdepth_new
from wikiapi_new.super.login_bots.cookies_bot import get_file_name
from wikiapi_new.super.super_login import Login
from wikiapi_new.super.login_bots.cookies_bot import get_cookies
from wikiapi_new.super.login_bots.cookies_bot import get_file_name

"""
from .S_API import bot_api
from .S_Login import super_login
from .S_Page import super_page
from .S_Category import catdepth_new

__all__ = [
    'bot_api',
    'super_page',
    'super_login',
    'catdepth_new',
    'S_API',
]
