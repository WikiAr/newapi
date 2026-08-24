""" """

from __future__ import annotations

import logging
import os
from typing import Any

import wikitextparser as wtp

logger = logging.getLogger(__name__)

STOP_EDIT_TEMPLATES: dict[str, list[str]] = {
    "all": ["تحرر", "قيد التطوير", "يحرر", "تطوير مقالة"],
    "تعريب": ["لا للتعريب"],
    "تقييم آلي": ["لا للتقييم الآلي"],
    "reftitle": ["لا لعنونة مرجع غير معنون"],
    "fixref": ["لا لصيانة المراجع"],
    "cat": ["لا للتصنيف المعادل"],
    "stub": ["لا لتخصيص البذرة"],
    "tempcat": ["لا لإضافة صناديق تصفح معادلة"],
    "portal": ["لا لربط البوابات المعادل", "لا لصيانة البوابات"],
}

BOT_USERNAME = os.getenv("WIKIPEDIA_BOT_USERNAME", "Mr.Ibrahembot")
bot_edit_cache = {}


def template_text_to_params(text: str) -> dict[str, str]:
    """
    Convert template text to params dict.
    """
    parsed = wtp.parse(text)
    if not parsed.templates:
        return {}
    params: dict[str, str] = {
        str(param.name).strip(): str(param.value).strip() for param in parsed.templates[0].arguments
    }
    return {x: v for x, v in params.items() if x and v}


class IsAllowed:
    def __init__(
        self,
        bot_username: str,
        text: str = "",
        title_page: str = "",
        bot_script: str = "all",
    ) -> None:
        self.bot_username = bot_username
        self.text = text
        self.title_page = title_page
        self.bot_script = bot_script

    def check(self) -> bool:
        """
        Determines if a bot is permitted to edit a page based on templates in the page text.
        """
        all_stop = STOP_EDIT_TEMPLATES["all"]

        parser = wtp.parse(self.text)
        templates = parser.templates

        # default if no restricting template found
        allowed_status = True

        for template in templates:
            title = str(template.normal_name()).strip().lower()

            restrictions = STOP_EDIT_TEMPLATES.get(self.bot_script, [])

            if title in restrictions or title in all_stop:
                logger.debug(f"the page has temp:({title}), bot_script:{self.bot_script} skipp.")
                allowed_status = False
                break

        if not allowed_status:
            return allowed_status

        for template in templates:
            title = str(template.normal_name()).strip().lower()

            if title == "nobots" or title == "bots":
                params: dict[str, Any] = {
                    str(param.name).strip(): str(param.value).strip()
                    for param in template.arguments
                    if str(param.value).strip()
                }

                _template = template.string

                if title == "nobots":
                    logger.debug(f"the page has temp:({_template}), bot_script:{self.bot_script}.")
                    allowed_status = self.handle_nobots_template(params)
                    if not allowed_status:
                        break

                elif title == "bots":
                    logger.debug(f"the page has temp:({_template}), bot_script:{self.bot_script}.")
                    allowed_status = self.handle_bots_template(params)
                    if not allowed_status:
                        break

        return allowed_status

    def is_included(self, arg_value: str, title: str, param: str) -> bool:
        value = [x.strip() for x in arg_value.split(",")]
        is_in = "all" in value or self.bot_username in value
        if is_in:
            logger.warning(f"Template:({title}) has |{param}={','.join(value)}.")
        return is_in

    def handle_deny_and_allow(
        self,
        temp_title: str,
        deny_param: str | None = None,
        allow_param: str | None = None,
    ) -> bool:
        """
        Both (Bots/Nobots) templates use the same logic in (deny/allow) params.

        # {{Bots|allow=<botlist>}} is the same as {{Nobots|allow=<botlist>}}

        # {{bots|allow=<botlist>}}      Block all bots not on the list.
        # {{bots|deny=<botlist>}}       Block all bots on the list.
        # {{bots|deny=<botlist>}}       Block all bots on the list.

        # {{bots|allow=BOT1|deny=BOT2}} Block BOT2 bot, allow BOT1 bot

        # {{bots|allow=all}}            Allow all bots
        # {{bots|allow=none}}           Block all bots
        # {{bots|deny=all}}             Block all bots

        """
        allowed = True
        if allow_param:
            allowed = self.is_included(allow_param, temp_title, "allow")

        if deny_param:
            allowed = allowed and not self.is_included(deny_param, temp_title, "deny")

        return allowed

    def handle_nobots_template(self, params: dict[str, str]) -> bool:
        """
        Handle nobots template logic.

        # {{nobots}}                        Block all bots
        # {{nobots|all}}                    Block all bots
        # {{nobots|BOT_NAME, BOT_NAME2}}    Block `BOT_NAME` and `BOT_NAME2` bots
        """
        if not params:
            logger.debug("nobots active - blocking bot")
            return False

        if params.get("1"):
            arg_value = params.get("1", "")
            return not self.is_included(arg_value, "nobots", "1")

        if params.get("deny") or params.get("allow"):
            return self.handle_deny_and_allow(
                temp_title="nobots",
                deny_param=params.get("deny"),
                allow_param=params.get("allow"),
            )
        # no restricting template found
        return True

    def handle_bots_template(self, params: dict[str, str]) -> bool:
        """
        Handle bots template logic.

        # {{bots}}                      Allow all bots

        # {{bots|allowscript=all}}      Allow all bots and all scripts
        # {{bots|denyscript=all}}       Block all scripts

        # {{bots|allowscript=ref}}      Allow ref script
        # {{bots|denyscript=ref}}       Block ref script
        """
        logger.debug(f"handling bots template for:(bots), params:({str(params)}).")

        if not params:
            return True

        if params.get("deny") or params.get("allow"):
            return self.handle_deny_and_allow(
                temp_title="bots",
                deny_param=params.get("deny"),
                allow_param=params.get("allow"),
            )

        return True


def handle_bots_template(text: str, bot_username: str = BOT_USERNAME) -> bool:
    bot = IsAllowed(
        bot_username=bot_username,
        text=text,
        title_page="test",
        bot_script="",
    )
    params = template_text_to_params(text)

    return bot.handle_bots_template(params)


def handle_nobots_template(text: str, bot_username: str = BOT_USERNAME) -> bool:
    bot = IsAllowed(
        bot_username=bot_username,
        text=text,
        title_page="test",
        bot_script="",
    )
    params = template_text_to_params(text)
    return bot.handle_nobots_template(params)


def is_bot_edit_allowed(
    text: str = "",
    title_page: str = "",
    bot_script: str = "all",
    use_cache: bool = True,
) -> bool:
    """
    Determines if a bot is permitted to edit a page based on templates in the page text.
    """
    if bot_script in ["", "fixref|cat|stub|tempcat|portal"]:
        bot_script = "all"

    if use_cache:
        bot_edit_cache.setdefault(bot_script, {})

        if title_page in bot_edit_cache[bot_script]:
            return bot_edit_cache[bot_script][title_page]

    bot = IsAllowed(
        bot_username=BOT_USERNAME,
        text=text,
        title_page=title_page,
        bot_script=bot_script,
    )
    allowed_status = bot.check()

    if use_cache:
        bot_edit_cache[bot_script][title_page] = allowed_status
    return allowed_status


__all__ = [
    "is_bot_edit_allowed",
    "handle_nobots_template",
    "handle_bots_template",
]
