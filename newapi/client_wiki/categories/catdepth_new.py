""" """

import functools
import logging

from ...utils import function_timer
from ..constants import CATEGORY_PREFIXES
from .category_db import CategoryDepth

logger = logging.getLogger(__name__)

SITECODE = "en"
FAMILY = "wikipedia"


@functools.lru_cache(maxsize=256)
def title_process(title: str, sitecode: str) -> str:
    prefixes = CATEGORY_PREFIXES
    start_prefixes = prefixes.get(sitecode)

    if start_prefixes and not title.startswith(start_prefixes):
        title = start_prefixes + title

    return title


def args_group(title: str, kwargs: dict) -> dict:
    args2 = {
        "title": title,
        "depth": None,
        "ns": None,
        "nslist": None,
        "onlyns": None,
        "without_lang": None,
        "with_lang": None,
        "tempyes": None,
        "props": None,
        "only_titles": None,
    }

    for k, v in kwargs.items():
        if k not in args2 or args2[k] is None:
            args2[k] = v

    return args2


@function_timer
def subcatquery(login_bot, title: str, sitecode: str = SITECODE, family: str = FAMILY, **kwargs) -> dict:
    print_s = kwargs.get("print_s", True)
    get_revids = kwargs.get("get_revids", False)

    title = title_process(title, sitecode)
    args2 = args_group(title, kwargs)

    if print_s:
        logger.debug(
            f"<<lightyellow>> catdepth_new.py sub cat query for {sitecode}:{title}, depth:{args2['depth']}, ns:{args2['ns']}, onlyns:{args2['onlyns']}"
        )

    logger.info(f"starting subcategory query: {sitecode}:{title}")
    bot = CategoryDepth(login_bot, title, **kwargs)
    result = bot.subcatquery_()

    if get_revids:
        result = bot.get_revids()

    if print_s:
        lenpages = bot.get_len_pages()
        logger.debug(
            f"<<lightblue>> find {len(result)} pages({args2['ns']}) in {sitecode}:{title}, depth:{args2['depth']} | {lenpages=}"
        )

    return result


__all__ = [
    "CategoryDepth",
    "subcatquery",
    "title_process",
    "args_group",
]
