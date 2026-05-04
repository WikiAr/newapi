""" """

import logging
import sys

import pywikibot

from ..config import settings

logger = logging.getLogger(__name__)
_save_or_ask: dict[str, bool] = {}


def showDiff(text_a: str, text_b: str) -> None:
    if "nodiff" in sys.argv:
        return
    pywikibot.showDiff(text_a, text_b)


class AskBot:
    def __init__(self) -> None:
        pass

    def ask_put(
        self,
        nodiff: bool = False,
        newtext: str = "",
        text: str = "",
        message: str = "",
        job: str = "General",
        username: str = "",
        summary: str = "",
    ) -> bool:
        """
        Prompts the user to confirm saving changes to a page, optionally displaying a diff.
        """
        message = message or "Do you want to accept these changes?"
        if settings.bot.ask and not _save_or_ask.get(job):
            if text or newtext:
                if not settings.bot.no_diff and not nodiff:
                    if len(newtext) < 70000 and len(text) < 70000 or settings.bot.show_diff:
                        showDiff(text, newtext)
                    else:
                        logger.warning("showDiff error..")
                logger.warning(f"diference in bytes: {len(newtext) - len(text):,}")
                logger.warning(f"len of text: {len(text):,}, len of newtext: {len(newtext):,}")
            if summary:
                logger.warning(f"-Edit summary: {summary}")
            logger.warning(f"<<lightyellow>>AskBot: {message}? (yes, no) {username=}")
            sa = input("([y]es, [N]o, [a]ll)?")
            if sa == "a":
                _save_or_ask[job] = True
                logger.warning("<<lightgreen>> ---------------------------------")
                logger.warning(f"<<lightgreen>> save all:{job} without asking.")
                logger.warning("<<lightgreen>> ---------------------------------")
            if sa not in ["y", "a", "", "Y", "A", "all", "aaa"]:
                logger.warning("wrong answer")
                return False
        return True


__all__ = [
    "AskBot",
    "showDiff",
]
