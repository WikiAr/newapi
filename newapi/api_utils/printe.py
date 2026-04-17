""" """

import logging
import sys
import pywikibot

logger = logging.getLogger(__name__)


def showDiff(text_a: str, text_b: str, context: int = 0) -> None:
    if "nodiff" in sys.argv:
        return
    pywikibot.showDiff(text_a, text_b)


def output(textm, *args, **kwargs):
    if "noprint" in sys.argv and not kwargs.get("p", False):
        return
    logger.info(textm)


def error(text, *args, **kwargs):
    text = f"<<red>> {str(text)} <<default>>"
    logger.error(text)


def info(text, *args, **kwargs):
    logger.info(text)


def warn(text, *args, **kwargs):
    logger.warning(text)


def warning(text, *args, **kwargs):
    logger.warning(text)


def debug(text, *args, **kwargs):
    logger.debug(text)


def test_print(text, *args, **kwargs):
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
