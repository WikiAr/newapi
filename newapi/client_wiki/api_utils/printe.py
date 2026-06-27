""" """

import logging

import pywikibot

from ...config import settings

logger = logging.getLogger(__name__)


def showDiff(text_a: str, text_b: str, context: int = 0) -> None:
    if settings.bot.no_diff:
        return
    pywikibot.showDiff(text_a, text_b)


def output(textm, *args, **kwargs) -> None:
    if settings.bot.no_print and not kwargs.get("p", False):
        return
    logger.info(textm)


def error(text: str, *args, **kwargs) -> None:
    text = f"<<red>> {str(text)} <<default>>"
    logger.error(text)


def info(text: str, *args, **kwargs) -> None:
    logger.info(text)


def warn(text: str, *args, **kwargs) -> None:
    logger.warning(text)


def warning(text: str, *args, **kwargs) -> None:
    logger.warning(text)


def debug(text: str, *args, **kwargs) -> None:
    logger.debug(text)


def test_print(text: str, *args, **kwargs) -> None:
    logger.debug(text)


__all__ = [
    "showDiff",
    "output",
    "debug",
    "warn",
    "error",
    "info",
    "test_print",
]
