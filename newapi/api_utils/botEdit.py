"""
from newapi.api_utils import botEdit
bot_edit!
"""

#
#
import datetime
import logging
import sys

logger = logging.getLogger(__name__)
from . import txtlib

# ---
edit_username = {1: "Mr.Ibrahembot"}
# ---
Bot_Cache = {}
Created_Cache = {}
# ---
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
        logger.info(
            f"<<lightred>> botEdit.py: the page has temp:({_template}), botjob:{botjob} skipp."
        )
        # printe.output( 'return False 2 ' )
        Bot_Cache[botjob][title_page] = False
        return False
    elif params.get("1"):
        List = [x.strip() for x in params.get("1", "").split(",")]
        # if 'all' in List or pywikibot.calledModuleName() in List or edit_username[1] in List:
        if "all" in List or edit_username[1] in List:
            logger.info(
                f"<<lightred>> botEdit.py: the page has temp:({_template}), botjob:{botjob} skipp."
            )
            # printe.output( 'return False 3 ' )
            # Bot_Cache[title_page] = False
            Bot_Cache[botjob][title_page] = False
            return False
    # ---
    # no restricting template found
    Bot_Cache[botjob][title_page] = True
    # ---
    return True


def _handle_bots_template(params, title_page, botjob, title):
    """Handle bots template logic."""
    # ---
    # printe.output( 'title == (%s) ' % title )
    # {{bots}}                  السماح لجميع البوتات
    if not params:
        Bot_Cache[botjob][title_page] = False
        return False
    else:
        logger.info(f"botEdit.py title:({title}), params:({str(params)}).")
        # for param in params:
        # value = params[param]
        # value = [ x.strip() for x in value.split(',') ]
        # ---
        # {{bots|allow=all}}      السماح لجميع البوتات
        # {{bots|allow=none}}     منع جميع البوتات
        allow = params.get("allow")
        if allow:
            value = [x.strip() for x in allow.split(",")]
            # if param == 'allow':
            # 'all' in value or edit_username[1] in value is True
            sd = "all" in value or edit_username[1] in value
            if not sd:
                logger.info(
                    f"<<lightred>>botEdit.py Template:({title}) has |allow={','.join(value)}."
                )
            else:
                logger.info(
                    f"<<lightgreen>>botEdit.py Template:({title}) has |allow={','.join(value)}."
                )
            Bot_Cache[botjob][title_page] = sd
            return sd
            # ---
        # ---
        # {{bots|deny=all}}      منع جميع البوتات
        deny = params.get("deny")
        if deny:
            value = [x.strip() for x in deny.split(",")]
            # {{bots|deny=all}}
            # if param == 'deny':
            sd = "all" not in value and edit_username[1] not in value
            if not sd:
                logger.info(
                    f"<<lightred>>botEdit.py Template:({title}) has |deny={','.join(value)}."
                )
            Bot_Cache[botjob][title_page] = sd
            return sd
        # ---
        # ---
        # if param == 'allowscript':
        # return ('all' in value or pywikibot.calledModuleName() in value)
        # if param == 'denyscript':
        # return not ('all' in value or pywikibot.calledModuleName() in value)
    # ---
    # no restricting template found
    Bot_Cache[botjob][title_page] = True
    # ---
    return True


def bot_May_Edit_do(text="", title_page="", botjob="all"):
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
    templates = txtlib.extract_templates_and_params(text)
    # ---
    all_stop = stop_edit_temps["all"]
    # ---
    for temp in templates:
        _name, namestrip, params, _template = (
            temp["name"],
            temp["namestrip"],
            temp["params"],
            temp["item"],
        )
        title = namestrip
        # ---
        # printe.output( '<<lightred>>botEdit.py title:(%s), params:(%s).' % ( title,str(params) ) )
        # ---
        restrictions = stop_edit_temps.get(botjob, [])
        # ---
        if title in restrictions or title in all_stop:
            logger.info(
                f"<<lightred>> botEdit.py: the page has temp:({title}), botjob:{botjob} skipp."
            )
            Bot_Cache[botjob][title_page] = False
            return False
        # ---
        # printe.output( '<<lightred>>botEdit.py title:(%s), params:(%s).' % ( title,str(params) ) )
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


def check_create_time(page, title_page):
    # ---
    """
    Checks if a page was created at least three hours ago before allowing bot edits.

    Returns True if the page is not in the Arabic main namespace or if the creation timestamp is missing. Returns False if the page was created less than three hours ago, caching the result for future checks.
    """
    # ---
    if title_page in Created_Cache:
        return Created_Cache[title_page]
    # ---
    ns = page.namespace()
    lang = page.lang
    # ---
    if ns != 0 or lang != "ar":
        return True
    # ---
    now = datetime.datetime.now(datetime.timezone.utc)
    # ---
    create_data = (
        page.get_create_data()
    )  # { "timestamp" : "2025-05-07T12:00:17Z", "user" : "", "anon" : "" }
    # ---
    delay_hours = 3
    # ---
    if create_data.get("timestamp"):
        # ---
        create_time = create_data["timestamp"]
        ts_c_time = datetime.datetime.strptime(
            create_time, "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=datetime.timezone.utc)
        # ---
        diff = (now - ts_c_time).total_seconds() / (60 * 60)
        # ---
        user = create_data.get("user", "")
        # ---
        wait_time = delay_hours - diff
        # ---
        if diff < delay_hours:
            logger.info(f"<<yellow>>Page:{title_page} create at ({create_time}).")
            logger.info(
                f"<<invert>>Page Created before {diff:.2f} hours by: {user}, wait {wait_time:.2f}H."
            )
            return False
    # ---
    return True


def check_last_edit_time(page, title_page, delay):
    # ---
    """
    Checks if enough time has passed since the last non-bot edit before allowing a bot to edit.

    If the last editor is a bot, editing is allowed immediately. Otherwise, returns False if the last edit was made less than the specified delay (in minutes) ago; returns True if the delay has passed or if no last edit timestamp is available.

    Args:
        page: The page object to check.
        title_page: The title of the page.
        delay: Minimum number of minutes that must have passed since the last edit.
    """
    userinfo = page.get_userinfo()
    # ---
    if "bot" in userinfo.get("groups", []):
        return True
    # ---
    # example: 2025-05-07T12:00:17Z
    timestamp = page.get_timestamp()
    # ---
    now = datetime.datetime.now(datetime.timezone.utc)
    # ---
    if timestamp:
        ts_time = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc
        )
        # ---
        diff_minutes = (now - ts_time).total_seconds() / 60
        # ---
        # printe.output(f"<<grey>> last-edit Δ={diff_minutes:.2f} min for {title_page}")
        # ---
        wait_time = delay - diff_minutes
        # ---
        if diff_minutes < delay:
            logger.info(f"<<yellow>>Page:{title_page} last edit ({timestamp}).")
            logger.info(
                f"<<invert>>Page Last edit before {delay} minutes, Wait {wait_time:.2f} minutes. title:{title_page}"
            )
            return False
    # ---
    return True


def bot_May_Edit(text="", title_page="", botjob="all", page=False, delay=0):
    # ---
    """
    Determines whether a bot is permitted to edit a page based on templates, last edit time, and creation time.

    If a page object is provided and template checks pass, the function also verifies that the page was not edited or created too recently, applying namespace and language restrictions for time-based checks.

    Args:
        text: The page text to analyze for edit-blocking templates.
        title_page: The title of the page being checked.
        botjob: The bot job type, used to determine relevant template restrictions.
        page: The page object, required for time-based checks.
        delay: Minimum number of minutes since the last edit required before editing.

    Returns:
        True if the bot is allowed to edit the page; False otherwise.
    """
    check_it = bot_May_Edit_do(text=text, title_page=title_page, botjob=botjob)
    # ---
    if page and check_it:
        # ---
        if delay and isinstance(delay, int):
            # ---
            ns = page.namespace()
            lang = page.lang
            # ---
            if ns != 0 or lang != "ar":
                return check_it
            # ---
            check_time = check_last_edit_time(page, title_page, delay)
            # ---
            if not check_time:
                return False
        # ---
        check_create = check_create_time(page, title_page)
        # ---
        Created_Cache[title_page] = check_create
        # ---
        if not check_create:
            return False
    # ---
    return check_it


def botMayEdit(**kwargs):
    return bot_May_Edit(**kwargs)


# ---
# python3 core8/pwb.py API/botEdit
# ---
if __name__ == "__main__":
    texts = """
{{Bots|deny=all}}
{{يتيمة|تاريخ=مايو 2020}}
{{صندوق معلومات شخص
| الصورة = Correggio, Alexandru Bogdan-Piteşti.jpg
}}"""
    fg = bot_May_Edit(text=texts)
    print(fg)
# ---
