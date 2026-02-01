"""
from newapi.api_utils import botEdit
bot_edit!
"""

#
#
import logging
import sys

import wikitextparser as wtp

logger = logging.getLogger(__name__)
edit_username = {1: "Mr.Ibrahembot"}
Bot_Cache = {}
stop_edit_temps = {
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


def _handle_nobots_template(params, title_page, botjob, _template):
    """Handle nobots template logic."""
    # ---
    # {{nobots}}                منع جميع البوتات
    # منع جميع البوتات
    if not params:
        logger.info(f"<<lightred>> botEdit.py: the page has template:({_template}), botjob:{botjob} skipp.")
        Bot_Cache[botjob][title_page] = False
        return False
    elif params.get("1"):
        List = [x.strip() for x in params.get("1", "").split(",")]
        # if 'all' in List or pywikibot.calledModuleName() in List or edit_username[1] in List:
        if "all" in List or edit_username[1] in List:
            logger.info(f"<<lightred>> botEdit.py: the page has template:({_template}), botjob:{botjob} skipp.")
            Bot_Cache[botjob][title_page] = False
            return False
    # ---
    Bot_Cache[botjob][title_page] = True
    # ---
    return True


def _handle_bots_template(params, title_page, botjob, title):
    """Handle bots template logic."""
    # ---
    # {{bots}}                  السماح لجميع البوتات
    if not params:
        Bot_Cache[botjob][title_page] = False
        return False
    else:
        logger.info(f"botEdit.py title:({title}), params:({str(params)}).")
        # ---
        # {{bots|allow=all}}      السماح لجميع البوتات
        # {{bots|allow=none}}     منع جميع البوتات
        allow = params.get("allow")
        if allow:
            value = [x.strip() for x in allow.split(",")]
            sd = "all" in value or edit_username[1] in value
            if not sd:
                logger.info(f"<<lightred>>botEdit.py Template:({title}) has |allow={','.join(value)}.")
            else:
                logger.info(f"<<lightgreen>>botEdit.py Template:({title}) has |allow={','.join(value)}.")
            Bot_Cache[botjob][title_page] = sd
            return sd
            # ---
        # ---
        # {{bots|deny=all}}      منع جميع البوتات
        deny = params.get("deny")
        if deny:
            value = [x.strip() for x in deny.split(",")]
            sd = "all" not in value and edit_username[1] not in value
            if not sd:
                logger.info(f"<<lightred>>botEdit.py Template:({title}) has |deny={','.join(value)}.")
            Bot_Cache[botjob][title_page] = sd
            return sd
        # ---
        # if param == 'allowscript':
        # return ('all' in value or pywikibot.calledModuleName() in value)
        # if param == 'denyscript':
        # return not ('all' in value or pywikibot.calledModuleName() in value)
    # ---
    Bot_Cache[botjob][title_page] = True
    # ---
    return True


def is_bot_edit_allowed(text="", title_page="", botjob="all"):
    # ---
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
    if ("botedit" in sys.argv or "editbot" in sys.argv) or "workibrahem" in sys.argv:
        return True
    # ---
    if botjob in ["", "fixref|cat|stub|tempcat|portal"]:
        botjob = "all"
    # ---
    if botjob not in Bot_Cache:
        Bot_Cache[botjob] = {}
    # ---
    if title_page in Bot_Cache[botjob]:
        return Bot_Cache[botjob][title_page]
    # ---
    all_stop = stop_edit_temps["all"]
    # ---
    parser = wtp.parse(text)
    templates = parser.templates
    # ---
    for template in templates:
        title = str(template.normal_name()).strip()
        # ---
        params = {
            str(param.name).strip(): str(param.value).strip()
            for param in template.arguments
            if str(param.value).strip()
        }
        # ---
        _template = template.string
        # ---
        restrictions = stop_edit_temps.get(botjob, [])
        # ---
        if title in restrictions or title in all_stop:
            logger.info(f"<<lightred>> botEdit.py: the page has template:({title}), botjob:{botjob} skipp.")
            Bot_Cache[botjob][title_page] = False
            return False
        # ---
        logger.debug("<<lightred>>botEdit.py title:(%s), params:(%s)." % (title, str(params)))
        # ---
        if title.lower() == "nobots":
            return _handle_nobots_template(params, title_page, botjob, _template)
        # ---
        # {{bots|allow=<botlist>}}  منع جميع البوتات غير الموجودة في القائمة
        # {{bots|deny=<botlist>}}   منع جميع البوتات الموجودة في القائمة
        # ---
        elif title.lower() == "bots":
            return _handle_bots_template(params, title_page, botjob, title)
    # ---
    # no restricting template found
    Bot_Cache[botjob][title_page] = True
    # ---
    return True


__all__ = [
    "is_bot_edit_allowed",
]
