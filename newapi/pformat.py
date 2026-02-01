"""
python3 core8/pwb.py newapi/pformat
"""

import sys
from pathlib import Path

import wikitextparser as wtp

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
