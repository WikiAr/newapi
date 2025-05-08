"""
bot_edit!
"""
#
#
import datetime
import sys
from newapi import printe
from newapi import txtlib

# ---
edit_username = {1: "Mr.Ibrahembot"}
# ---
Bot_Cash = {}
# ---
stop_edit_temps = {
    "all": ["تحرر", "قيد التطوير", "يحرر"],
    "تعريب": ["لا للتعريب"],
    "تقييم آلي": ["لا للتقييم الآلي"],
    "reftitle": ["لا لعنونة مرجع غير معنون"],
    "fixref": ["لا لصيانة المراجع"],
    "cat": ["لا للتصنيف المعادل"],
    "stub": ["لا لتخصيص البذرة"],
    "tempcat": ["لا لإضافة صناديق تصفح معادلة"],
    "portal": ["لا لربط البوابات المعادل", "لا لصيانة البوابات"],
}


def bot_May_Edit_do(text="", title_page="", botjob="all"):
    # ---
    if ("botedit" in sys.argv or "editbot" in sys.argv) or "workibrahem" in sys.argv:
        return True
    # ---
    if botjob in ["", "fixref|cat|stub|tempcat|portal"]:
        botjob = "all"
    # ---
    if botjob not in Bot_Cash:
        Bot_Cash[botjob] = {}
    # ---
    if title_page in Bot_Cash[botjob]:
        return Bot_Cash[botjob][title_page]
    # ---
    templates = txtlib.extract_templates_and_params(text)
    # ---
    all_stop = stop_edit_temps["all"]
    # ---
    for temp in templates:
        _name, namestrip, params, _template = temp["name"], temp["namestrip"], temp["params"], temp["item"]
        title = namestrip
        # ---
        # printe.output( '<<lightred>>botEdit.py title:(%s), params:(%s).' % ( title,str(params) ) )
        # ---
        restrictions = stop_edit_temps.get(botjob, [])
        # ---
        if title in restrictions or title in all_stop:
            printe.output(f"<<lightred>> botEdit.py: the page has temp:({title}), botjob:{botjob} skipp.")
            Bot_Cash[botjob][title_page] = False
            return False
        # ---
        # if title == 'Nobots' or title == 'nobots':
        if title.lower() in ["bots", "nobots"]:
            # ---
            # printe.output( '<<lightred>>botEdit.py title:(%s), params:(%s).' % ( title,str(params) ) )
            # ---
            if title.lower() == "nobots":
                # ---
                # {{nobots}}                منع جميع البوتات
                # منع جميع البوتات
                if not params:
                    printe.output(f"<<lightred>> botEdit.py: the page has temp:({_template}), botjob:{botjob} skipp.")
                    # printe.output( 'return False 2 ' )
                    Bot_Cash[botjob][title_page] = False
                    return False
                elif params.get("1"):
                    List = [x.strip() for x in params.get("1", "").split(",")]
                    # if 'all' in List or pywikibot.calledModuleName() in List or edit_username[1] in List:
                    if "all" in List or edit_username[1] in List:
                        printe.output(f"<<lightred>> botEdit.py: the page has temp:({_template}), botjob:{botjob} skipp.")
                        # printe.output( 'return False 3 ' )
                        # Bot_Cash[title_page] = False
                        Bot_Cash[botjob][title_page] = False
                        return False
            # ---
            # {{bots|allow=<botlist>}}  منع جميع البوتات غير الموجودة في القائمة
            # {{bots|deny=<botlist>}}   منع جميع البوتات الموجودة في القائمة
            # ---
            elif title.lower() == "bots":
                # printe.output( 'title == (%s) ' % title )
                # {{bots}}                  السماح لجميع البوتات
                if not params:
                    Bot_Cash[botjob][title_page] = False
                    return False
                else:
                    printe.output(f"botEdit.py title:({title}), params:({str(params)}).")
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
                            printe.output(f"<<lightred>>botEdit.py Template:({title}) has |allow={','.join(value)}.")
                        else:
                            printe.output(f"<<lightgreen>>botEdit.py Template:({title}) has |allow={','.join(value)}.")
                        Bot_Cash[botjob][title_page] = sd
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
                            printe.output(f"<<lightred>>botEdit.py Template:({title}) has |deny={','.join(value)}.")
                        Bot_Cash[botjob][title_page] = sd
                        return sd
                    # ---
                    # ---
                    # if param == 'allowscript':
                    # return ('all' in value or pywikibot.calledModuleName() in value)
                    # if param == 'denyscript':
                    # return not ('all' in value or pywikibot.calledModuleName() in value)
                    # ---
    # ---
    # no restricting template found
    Bot_Cash[botjob][title_page] = True
    # ---
    return True


def check_create_time(page, title_page):
    # ---
    """

    """

    ns = page.namespace()
    lang = page.lang
    # ---
    if ns != 0 or lang != "ar":
        return True
    # ---
    now = datetime.datetime.now(datetime.timezone.utc)
    # ---
    create_data = page.get_create_data()  # { "timestamp" : "2025-05-07T12:00:17Z", "user" : "", "anon" : "" }
    # ---
    delay = 3
    # ---
    if create_data.get("timestamp"):
        # ---
        create_time = create_data["timestamp"]
        ts_c_time = datetime.datetime.strptime(create_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        # ---
        diff = (now - ts_c_time).total_seconds() / (60 * 60)
        # ---
        # ---
        user = create_data.get("user", "")
        # ---
        wait_time = delay - diff
        # ---
        if diff < delay:
            printe.output(f"<<yellow>>Page:{title_page} create at ({create_time}).")
            printe.output(f"<<invert>>Page Created before {diff:.2f} hours by: {user}, wait {wait_time:.2f}H.")
            return False
    # ---
    return True


def check_last_edit_time(page, title_page, delay):
    # ---
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
# ---
