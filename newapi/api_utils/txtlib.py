#!/usr/bin/python3
"""

from . import txtlib
# txtlib.get_one_temp_params( text, templates=[], lowers=False )
# alltemp = txtlib.get_all_temps_params( text, templates=[], lowers=False )
# for tab in alltemp: for namestrip, params in tab.keys():
# ---
from . import txtlib
# temps = txtlib.extract_templates_and_params(text)
# for temp in temps: name, namestrip, params, template = temp['name'], temp['namestrip'], temp['params'], temp['item']

"""
# from ..other_bots import printe

from functools import lru_cache

import wikitextparser as wtp


@lru_cache(maxsize=512)
def extract_templates_and_params(text):
    # ---
    result = []
    # ---
    parsed = wtp.parse(text)
    templates = parsed.templates
    arguments = "arguments"
    # ---
    for template in templates:
        # ---
        params = {}
        for param in getattr(template, arguments):
            value = str(param.value)  # mwpfh needs upcast to str
            key = str(param.name)
            key = key.strip()
            params[key] = value
        # ---
        name = template.name.strip()
        # ---
        # print('=====')
        # ---
        name = str(template.normal_name()).strip()
        pa_item = template.string
        # printe.output( "<<lightyellow>> pa_item: %s" % pa_item )
        # ---
        namestrip = name
        # ---
        ficrt = {
            "name": f"قالب:{name}",
            "namestrip": namestrip,
            "params": params,
            "item": pa_item,
        }
        # ---
        result.append(ficrt)
    # ---
    return result


def get_one_temp_params(text, tempname="", templates=[], lowers=False, get_all_temps=False):
    ingr = extract_templates_and_params(text)
    # ---
    temps = templates
    # ---
    if tempname:
        temps.append(tempname)
    # ---
    temps = [x.replace("قالب:", "").replace("Template:", "").replace("_", " ").strip() for x in temps]
    # ---
    if lowers:
        temps = [x.lower() for x in temps]
    # ---
    named = {}
    # ---
    if get_all_temps:
        named = []
    # ---
    for temp in ingr:
        # ---
        # name, namestrip, params, template = temp['name'], temp['namestrip'], temp['params'], temp['item']
        namestrip, params = temp["namestrip"], temp["params"]
        # ---
        if lowers:
            namestrip = namestrip.lower()
        # ---
        if namestrip in temps:
            if not get_all_temps:
                return params
            # ---
            # print("te:%s, namestrip:%s" % (te,namestrip) )
            # ---
            tabe = {namestrip: params}
            named.append(tabe)
    # ---
    return named


def get_all_temps_params(text, templates=None, lowers=False):
    # ---
    if templates is None:
        templates = []
    # ---
    tab = get_one_temp_params(text, templates=templates, lowers=lowers, get_all_temps=True)
    # ---
    return tab


# ---
test_text = """
{{ص.م/صورة مضاعفة ويكي بيانات|معرف ويكي بيانات={{{معرف ويكي بيانات|}}}
| صورة1 ={{{علم|{{{flag|{{{صورة علم|}}}}}}}}}
| تعليق1 ={{#لو:{{قيمة ويكي بيانات|معرف ويكي بيانات={{{معرف ويكي بيانات|}}}|{{{وصف العلم|{{{flagcaption|}}}}}}|خاصية=P163|rank=best}}|{{قيمة ويكي بيانات|معرف ويكي بيانات={{{معرف ويكي بيانات|}}}|{{{وصف العلم|{{{flagcaption|}}}}}}|خاصية=P163|rank=best}}|{{فصع}}}}
| عرض1 ={{{عرض العلم|{{{flagsize|125}}}}}}
| صورة2 ={{{motto|{{{شعار|}}}}}}
| تعليق2 ={{#لو:{{قيمة ويكي بيانات|معرف ويكي بيانات={{{معرف ويكي بيانات|}}}|{{{تعليق الشعار|{{{وصف الشعار|}}}}}}|خاصية=P237|rank=best}}|{{قيمة ويكي بيانات|معرف ويكي بيانات={{{معرف ويكي بيانات|}}}|{{{تعليق الشعار|{{{وصف الشعار|}}}}}}|خاصية=P237|rank=best}}|{{فصع}}}}
| عرض2 = {{{عرض الشعار|125}}}
| خاصية1 =P41
| خاصية2 ={{#لو:{{#خاصية:P94}}|P94|P154}}
|خلفية={{{خلفية|}}}
}}

{{ourworldindatamirror|https://owidm.wmcloud.org/grapher/cancer-death-rates?tab=map {{Webarchive}}}}
"""
# ---
if __name__ == "__main__":
    # ---
    # ---
    ingr = extract_templates_and_params(test_text)
    for temp in ingr:
        # ---
        name, namestrip, params, template = temp["name"], temp["namestrip"], temp["params"], temp["item"]
        # ---
        print("-----------------------------")
        print(f"name: {name}")
        print(f"namestrip: {namestrip}")
        print(f"params: {params}")
        print(f"template: {template}")
