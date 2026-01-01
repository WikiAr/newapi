"""
python3 core8/pwb.py newapi/pformat
"""
import sys
import wikitextparser as wtp
from pathlib import Path
from .config import settings


# python3 core8/pwb.py newapi/pformat -title:قالب:Cycling_race/stageclassification3
# python3 core8/pwb.py newapi/pformat -title:قالب:معلومات_خاصية_ويكي_بيانات/تتبع
# python3 core8/pwb.py newapi/pformat -title:
# python3 core8/pwb.py newapi/pformat -title:
# python3 core8/pwb.py newapi/pformat -title:قالب:Interlanguage_link_multi
# python3 core8/pwb.py newapi/pformat -title:قالب:Cs1_wrapper


def make_new_text(text):
    # ---
    new_text = text
    # ---
    # Parse the wikitext
    temps = wtp.parse(text).templates
    # ---
    for temp in temps:
        temp_text = temp.string
        new_temp = temp.pformat(" ")
        new_text = new_text.replace(temp_text, new_temp)
    # ---
    return new_text


if __name__ == "__main__":
    # ---
    settings.flags.workibrahem = True
    settings.flags.ask = True
    # ---
    Dir = Path(__file__).parent
    # ---
    title = ''
    text = open(f"{Dir}/pformat.txt", "r", encoding="utf-8").read()
    for arg in sys.argv:
        arg, _, value = arg.partition(':')
        if arg == '-title' or arg == '-page':
            title = value
    # ---
    if title:
        # ---
        from newapi.page import MainPage

        page = MainPage(title, 'ar', family='wikipedia')
        text = page.get_text()
        newtext = make_new_text(text)
        if settings.flags.save:
            save_page = page.save(newtext=newtext, summary='', nocreate=1, minor='')
    else:
        prased = wtp.parse(text)
        newtext = prased.pformat()
    # ---
    print(newtext)
    # ---
    with open(f"{Dir}/pformat.txt", "w", encoding="utf-8") as logfile:
        logfile.write(newtext)
    # ---
    print('add "save" to sys.argv to save.')
    # ---
