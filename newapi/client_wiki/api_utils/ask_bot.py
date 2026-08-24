""" """

from __future__ import annotations

import logging

import pywikibot

logger = logging.getLogger(__name__)

_save_or_ask: dict[str, bool] = {}


class AskBot:
    def __init__(
        self,
        ask: bool | None = None,
        nodiff: bool | None = None,
    ) -> None:
        self.ask = ask if ask is not None else False
        self.nodiff = nodiff if nodiff is not None else False

    def ask_user(
        self,
        newtext: str = "",
        text: str | None = "",
        message: str = "",
        job: str = "General",
        username: str = "",
        summary: str = "",
    ) -> bool:
        """
        Prompts the user to confirm saving changes to a page, optionally displaying a diff.
        """
        message = message or "Do you want to accept these changes?"
        if _save_or_ask.get(job):
            return True

        if not self.ask:
            return True

        text = text or ""
        if text or newtext:
            if not self.nodiff:
                pywikibot.showDiff(text, newtext)

            logger.warning(f"diference in bytes: {len(newtext) - len(text):,}")
            logger.warning(f"len of text: {len(text):,}, len of newtext: {len(newtext):,}")

        if summary:
            logger.warning(f"-Edit summary: {summary}")

        logger.warning(f"AskBot: {message}? (yes, no) {username=}")

        sa = input("([y]es, [N]o, [a]ll)?")

        if sa == "a":
            _save_or_ask[job] = True
            logger.warning("---------------------------------")
        logger.warning(f"save all:{job} without asking.")
        logger.warning("---------------------------------")

        if sa not in ["y", "a", "", "Y", "A", "all", "aaa"]:
            logger.warning("wrong answer")
            return False

        return True


__all__ = [
    "AskBot",
]
