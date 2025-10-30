# -*- coding: utf-8 -*-
"""Public package interface for the :mod:`newapi` project."""

from .DB_bots import db_bot, pymysql_bot
from .accounts import useraccount
from .api_utils import botEdit, except_err, printe, txtlib, wd_sparql
from .super.login_wrap import LoginWrap
from . import page

__all__ = [
    "useraccount",
    "wd_sparql",
    "txtlib",
    "pymysql_bot",
    "db_bot",
    "botEdit",
    "except_err",
    "printe",
    "page",
    "LoginWrap",
    "__version__",
]

__version__ = "0.1.0"
