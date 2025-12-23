"""
from newapi.api_utils import botEdit
bot_edit!
"""
#
#
import datetime
import sys
from functools import lru_cache
from . import printe
from . import txtlib
# ---
edit_username = {1: "Mr.Ibrahembot"}
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


def _check_nobots_template(params, title_page, botjob, _template):
    """Check nobots template and return result."""
    # ---
    # {{nobots}}                منع جميع البوتات
    # منع جميع البوتات
    if not params:
        printe.output(f"<<lightred>> botEdit.py: the page has temp:({_template}), botjob:{botjob} skipp.")
        return False
    elif params.get("1"):
        List = [x.strip() for x in params.get("1", "").split(",")]
        if "all" in List or edit_username[1] in List:
            printe.output(f"<<lightred>> botEdit.py: the page has temp:({_template}), botjob:{botjob} skipp.")
            return False
    # ---
    return True


def _check_bots_template(params, title_page, botjob, title):
    """Check bots template and return result."""
    # ---
    # {{bots}}                  السماح لجميع البوتات
    if not params:
        return False
    else:
        printe.output(f"botEdit.py title:({title}), params:({str(params)}).")
        # ---
        # {{bots|allow=all}}      السماح لجميع البوتات
        # {{bots|allow=none}}     منع جميع البوتات
        allow = params.get("allow")
        if allow:
            value = [x.strip() for x in allow.split(",")]
            sd = "all" in value or edit_username[1] in value
            if not sd:
                printe.output(f"<<lightred>>botEdit.py Template:({title}) has |allow={','.join(value)}.")
            else:
                printe.output(f"<<lightgreen>>botEdit.py Template:({title}) has |allow={','.join(value)}.")
            return sd
        # ---
        # {{bots|deny=all}}      منع جميع البوتات
        deny = params.get("deny")
        if deny:
            value = [x.strip() for x in deny.split(",")]
            sd = "all" not in value and edit_username[1] not in value
            if not sd:
                printe.output(f"<<lightred>>botEdit.py Template:({title}) has |deny={','.join(value)}.")
            return sd
    # ---
    return True


@lru_cache(maxsize=1024)
def _bot_may_edit_cached(title_page, botjob, text):
    """
    Cached computation of whether a bot may edit a page.
    
    Uses functools.lru_cache for memoization. The cache key includes
    the full text to ensure correct results when page content changes.
    
    Note: Log messages inside this function will only appear on cache misses
    (i.e., when the result is computed for the first time for a given combination
    of arguments). This is intentional to avoid spamming logs with repeated warnings
    for the same page content.
    """
    templates = txtlib.extract_templates_and_params(text)
    # ---
    all_stop = stop_edit_temps["all"]
    # ---
    for temp in templates:
        _name, namestrip, params, _template = temp["name"], temp["namestrip"], temp["params"], temp["item"]
        title = namestrip
        # ---
        restrictions = stop_edit_temps.get(botjob, [])
        # ---
        if title in restrictions or title in all_stop:
            printe.output(f"<<lightred>> botEdit.py: the page has temp:({title}), botjob:{botjob} skipp.")
            return False
        # ---
        if title.lower() == "nobots":
            return _check_nobots_template(params, title_page, botjob, _template)
        # ---
        # {{bots|allow=<botlist>}}  منع جميع البوتات غير الموجودة في القائمة
        # {{bots|deny=<botlist>}}   منع جميع البوتات الموجودة في القائمة
        # ---
        elif title.lower() == "bots":
            return _check_bots_template(params, title_page, botjob, title)
    # ---
    # no restricting template found
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
    return _bot_may_edit_cached(title_page, botjob, text)


def _check_create_time(title_page, ns, lang, create_timestamp, user):
    """Check for page creation time (not cached due to time-dependent logic)."""
    if ns != 0 or lang != "ar":
        return True
    # ---
    if not create_timestamp:
        return True
    # ---
    now = datetime.datetime.now(datetime.timezone.utc)
    delay_hours = 3
    # ---
    ts_c_time = datetime.datetime.strptime(create_timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    # ---
    diff = (now - ts_c_time).total_seconds() / (60 * 60)
    # ---
    wait_time = delay_hours - diff
    # ---
    if diff < delay_hours:
        printe.output(f"<<yellow>>Page:{title_page} create at ({create_timestamp}).")
        printe.output(f"<<invert>>Page Created before {diff:.2f} hours by: {user}, wait {wait_time:.2f}H.")
        return False
    # ---
    return True


def check_create_time(page, title_page):
    # ---
    """
    Checks if a page was created at least three hours ago before allowing bot edits.

    Returns True if the page is not in the Arabic main namespace or if the creation timestamp is missing. Returns False if the page was created less than three hours ago.
    
    Note: This function is not cached because the result depends on the current time.
    """
    # ---
    ns = page.namespace()
    lang = page.lang
    # ---
    create_data = page.get_create_data()  # { "timestamp" : "2025-05-07T12:00:17Z", "user" : "", "anon" : "" }
    create_timestamp = create_data.get("timestamp", "")
    user = create_data.get("user", "")
    # ---
    return _check_create_time(title_page, ns, lang, create_timestamp, user)


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
        ts_time = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        # ---
        diff_minutes = (now - ts_time).total_seconds() / 60
        # ---
        # printe.output(f"<<grey>> last-edit Δ={diff_minutes:.2f} min for {title_page}")
        # ---
        wait_time = delay - diff_minutes
        # ---
        if diff_minutes < delay:
            printe.output(f"<<yellow>>Page:{title_page} last edit ({timestamp}).")
            printe.output(f"<<invert>>Page Last edit before {delay} minutes, Wait {wait_time:.2f} minutes. title:{title_page}")
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
