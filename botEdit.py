"""
bot_edit!
"""
#
#
import sys
from newapi import printe
from newapi import txtlib

# ---
edit_username = {
    1: "Mr.Ibrahembot"
}
# ---
Bot_Cash = {}
# ---
stop_edit_temps = {
    'all': ['تحرر', 'قيد التطوير', 'يحرر'],
    'fixref': ["لا لصيانة المراجع"],
    'cat': ["لا للتصنيف المعادل"],
    'stub': ["لا لتخصيص البذرة"],
    'tempcat': ["لا لإضافة صناديق تصفح معادلة"],
    'portal': ["لا لربط البوابات المعادل", 'لا لصيانة البوابات']
}


def bot_May_Edit(text='', title_page='', botjob='all'):
    """Determine if a bot may edit a given page based on templates.

    This function checks if the bot is allowed to edit a page by examining
    specific templates present in the page's content. It considers various
    conditions, such as the bot's job type and any restrictions defined by
    templates like 'nobots' and 'bots'. The function utilizes a cache to
    store results for previously checked pages to optimize performance.

    Args:
        text (str): The content of the page to be checked.
        title_page (str): The title of the page being checked.
        botjob (str): The type of job the bot is performing, which can affect
            its editing permissions.

    Returns:
        bool: True if the bot is allowed to edit the page, False otherwise.
    """

    # ---
    if ('botedit' in sys.argv or 'editbot' in sys.argv) or 'workibrahem' in sys.argv:
        return True
    # ---
    if botjob in ['', 'fixref|cat|stub|tempcat|portal']:
        botjob = 'all'
    # ---
    if botjob not in Bot_Cash:
        Bot_Cash[botjob] = {}
    # ---
    if title_page in Bot_Cash[botjob]:
        return Bot_Cash[botjob][title_page]
    # ---
    templates = txtlib.extract_templates_and_params(text)
    # ---
    all_stop = stop_edit_temps['all']
    # ---
    for temp in templates:
        _name, namestrip, params, _template = temp['name'], temp['namestrip'], temp['params'], temp['item']
        title = namestrip
        # ---
        # printe.output( '<<lightred>>botEdit.py title:(%s), params:(%s).' % ( title,str(params) ) )
        # ---
        restrictions = stop_edit_temps.get(botjob, [])
        # ---
        if title in restrictions or title in all_stop:
            printe.output(f'<<lightred>> botEdit.py: the page has temp:({title}), botjob:{botjob} skipp.')
            Bot_Cash[botjob][title_page] = False
            return False
        # ---
        # if title == 'Nobots' or title == 'nobots':
        if title.lower() in ['bots', 'nobots']:
            # ---
            # printe.output( '<<lightred>>botEdit.py title:(%s), params:(%s).' % ( title,str(params) ) )
            # ---
            if title.lower() == 'nobots':
                # ---
                # {{nobots}}                منع جميع البوتات
                # منع جميع البوتات
                if not params:
                    printe.output(f'<<lightred>> botEdit.py: the page has temp:({_template}), botjob:{botjob} skipp.')
                    # pywikibot.output( 'return False 2 ' )
                    Bot_Cash[botjob][title_page] = False
                    return False
                elif params.get('1'):
                    List = [x.strip() for x in params.get('1', '').split(',')]
                    # if 'all' in List or pywikibot.calledModuleName() in List or edit_username[1] in List:
                    if 'all' in List or edit_username[1] in List:
                        printe.output(f'<<lightred>> botEdit.py: the page has temp:({_template}), botjob:{botjob} skipp.')
                        # pywikibot.output( 'return False 3 ' )
                        Bot_Cash[title_page] = False
                        return False
            # ---
            # {{bots|allow=<botlist>}}  منع جميع البوتات غير الموجودة في القائمة
            # {{bots|deny=<botlist>}}   منع جميع البوتات الموجودة في القائمة
            # ---
            elif title.lower() == 'bots':
                # printe.output( 'title == (%s) ' % title )
                # {{bots}}                  السماح لجميع البوتات
                if not params:
                    Bot_Cash[botjob][title_page] = False
                    return False
                else:
                    printe.output(f'botEdit.py title:({title}), params:({str(params)}).')
                    # for param in params:
                    # value = params[param]
                    # value = [ x.strip() for x in value.split(',') ]
                    # ---
                    # {{bots|allow=all}}      السماح لجميع البوتات
                    # {{bots|allow=none}}     منع جميع البوتات
                    allow = params.get('allow')
                    if allow:
                        value = [x.strip() for x in allow.split(',')]
                        # if param == 'allow':
                        # 'all' in value or edit_username[1] in value is True
                        sd = 'all' in value or edit_username[1] in value
                        if not sd:
                            printe.output(f"<<lightred>>botEdit.py Template:({title}) has |allow={','.join(value)}.")
                        else:
                            printe.output(f"<<lightgreen>>botEdit.py Template:({title}) has |allow={','.join(value)}.")
                        Bot_Cash[botjob][title_page] = sd
                        return sd
                        # ---
                    # ---
                    # {{bots|deny=all}}      منع جميع البوتات
                    deny = params.get('deny')
                    if deny:
                        value = [x.strip() for x in deny.split(',')]
                        # {{bots|deny=all}}
                        # if param == 'deny':
                        sd = 'all' not in value and edit_username[1] not in value
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


# ---
# python3 core8/pwb.py API/botEdit
# ---
if __name__ == '__main__':
    texts = '''
{{Bots|deny=all}}
{{يتيمة|تاريخ=مايو 2020}}
{{صندوق معلومات شخص
| الصورة = Correggio, Alexandru Bogdan-Piteşti.jpg
}}'''
    fg = bot_May_Edit(text=texts)
    print(fg)
# ---
