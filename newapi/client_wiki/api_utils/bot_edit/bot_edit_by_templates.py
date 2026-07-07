""" """

import logging

import wikitextparser as wtp

from ....config import settings

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

BOT_USERNAME = "Mr.Ibrahembot"
Bot_Cache = {}


def _handle_nobots_template(params, title_page, botjob, _template) -> bool:
    """Handle nobots template logic."""
    # {{nobots}}                منع جميع البوتات
    # منع جميع البوتات
    if not params:
        logger.debug(f"<<lightred>> botEdit.py: the page has temp:({_template}), botjob:{botjob} skipp.")
        logger.debug(f"nobots active - blocking bot {botjob} on {title_page}")
        Bot_Cache[botjob][title_page] = False
        return False
    elif params.get("1"):
        list_data = [x.strip() for x in params.get("1", "").split(",")]
        # if 'all' in List or pywikibot.calledModuleName() in List or BOT_USERNAME in List:
        if "all" in list_data or BOT_USERNAME in list_data:
            logger.debug(f"<<lightred>> botEdit.py: the page has temp:({_template}), botjob:{botjob} skipp.")
            logger.debug(f"bot {BOT_USERNAME} in nobots list - blocking {title_page}")
            # Bot_Cache[title_page] = False
            Bot_Cache[botjob][title_page] = False
            return False
    # no restricting template found
    Bot_Cache[botjob][title_page] = True
    return True


def _handle_bots_template(params, title_page, botjob, title):
    """Handle bots template logic."""
    logger.debug(f"handling bots template for {title}")
    # {{bots}}                  السماح لجميع البوتات
    if not params:
        Bot_Cache[botjob][title_page] = False
        return False
    else:
        logger.debug(f"botEdit.py title:({title}), params:({str(params)}).")
        # for param in params:
        # value = params[param]
        # value = [ x.strip() for x in value.split(',') ]
        # {{bots|allow=all}}      السماح لجميع البوتات
        # {{bots|allow=none}}     منع جميع البوتات
        allow = params.get("allow")
        if allow:
            value = [x.strip() for x in allow.split(",")]
            # if param == 'allow':
            # 'all' in value or BOT_USERNAME in value is True
            sd = "all" in value or BOT_USERNAME in value
            if not sd:
                logger.debug(f"<<lightred>>botEdit.py Template:({title}) has |allow={','.join(value)}.")
            else:
                logger.warning(f"<<lightgreen>>botEdit.py Template:({title}) has |allow={','.join(value)}.")
            Bot_Cache[botjob][title_page] = sd
            return sd
        # {{bots|deny=all}}      منع جميع البوتات
        deny = params.get("deny")
        if deny:
            value = [x.strip() for x in deny.split(",")]
            # {{bots|deny=all}}
            # if param == 'deny':
            sd = "all" not in value and BOT_USERNAME not in value
            if not sd:
                logger.debug(f"<<lightred>>botEdit.py Template:({title}) has |deny={','.join(value)}.")
            Bot_Cache[botjob][title_page] = sd
            return sd
        # if param == 'allowscript':
        # return ('all' in value or pywikibot.calledModuleName() in value)
        # if param == 'denyscript':
        # return not ('all' in value or pywikibot.calledModuleName() in value)
    # no restricting template found
    Bot_Cache[botjob][title_page] = True
    return True


def is_bot_edit_allowed(
    text: str = "",
    title_page: str = "",
    botjob: str = "all",
) -> bool:
    """
    Determines if a bot is permitted to edit a page based on templates in the page text.

    Checks for the presence of templates that restrict bot editing, such as those in the stop lists for the specified bot job or the global list. Handles special cases for `nobots` and `bots` templates, interpreting their parameters to allow or deny editing for specific bots or all bots. Results are cached for efficiency.

    Args:
        text: The wikitext of the page to analyze.
        title_page: The title of the page.
        botjob: The bot job type, used to select relevant stop templates.

    Returns:
        True if the bot is allowed to edit the page; False otherwise.
    """
    if (settings.bot.force_edit) or settings.bot.workibrahem:
        return True

    if botjob in ["", "fixref|cat|stub|tempcat|portal"]:
        botjob = "all"

    if botjob not in Bot_Cache:
        Bot_Cache[botjob] = {}

    if title_page in Bot_Cache[botjob]:
        return Bot_Cache[botjob][title_page]

    all_stop = STOP_EDIT_TEMPLATES["all"]

    parser = wtp.parse(text)
    templates = parser.templates

    for template in templates:
        title = str(template.normal_name()).strip()

        params = {
            str(param.name).strip(): str(param.value).strip()
            for param in template.arguments
            if str(param.value).strip()
        }

        _template = template.string

        restrictions = STOP_EDIT_TEMPLATES.get(botjob, [])

        if title in restrictions or title in all_stop:
            logger.debug(f"<<lightred>> botEdit.py: the page has temp:({title}), botjob:{botjob} skipp.")
            Bot_Cache[botjob][title_page] = False
            return False

        # logger.debug("<<lightred>>botEdit.py title:(%s), params:(%s)." % (title, str(params)))

        if title.lower() == "nobots":
            return _handle_nobots_template(params, title_page, botjob, _template)

        # {{bots|allow=<botlist>}}  منع جميع البوتات غير الموجودة في القائمة
        # {{bots|deny=<botlist>}}   منع جميع البوتات الموجودة في القائمة

        elif title.lower() == "bots":
            return _handle_bots_template(params, title_page, botjob, title)

    # no restricting template found
    Bot_Cache[botjob][title_page] = True
    return True


__all__ = [
    "is_bot_edit_allowed",
    "BOT_USERNAME",
]
