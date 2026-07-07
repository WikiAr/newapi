#!/usr/bin/python3
""" """

import logging
from functools import lru_cache
from typing import Any

import wikitextparser as wtp

logger = logging.getLogger(__name__)


@lru_cache(maxsize=512)
def extract_templates_and_params(text: str) -> list[dict[str, Any]]:
    # ---
    result = []
    # ---
    if not text or not isinstance(text, str):
        return result
    # ---
    parsed = wtp.parse(text)
    # ---
    for template in parsed.templates:
        # ---
        if not template:
            continue
        # ---
        params = {}
        for param in template.arguments:
            value = str(param.value)  # mwpfh needs upcast to str
            key = str(param.name)
            key = key.strip()
            params[key] = value
        # ---
        name = template.name.strip()
        # ---
        name = str(template.normal_name()).strip()
        pa_item = template.string
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


def get_one_temp_params(
    text: str,
    tempname: str = "",
    templates=None,
    lowers: bool = False,
    get_all_temps: bool = False,
) -> Any | list[Any] | dict[Any, Any]:
    ingr = extract_templates_and_params(text)
    # ---
    temps = list(templates) if templates is not None else []
    # ---
    if tempname:
        temps.append(tempname)
    # ---
    temps = [x.replace("قالب:", "").replace("Template:", "").replace("_", " ").strip() for x in temps]
    # ---
    if lowers:
        temps = [x.lower() for x in temps]
    # ---
    named = [] if get_all_temps else {}
    # ---
    for temp in ingr:
        # ---
        namestrip, params = temp["namestrip"], temp["params"]
        # ---
        if lowers:
            namestrip = namestrip.lower()
        # ---
        if namestrip in temps:
            if not get_all_temps:
                return params
            tabe = {namestrip: params}

            if isinstance(named, list):
                named.append(tabe)
            else:
                named.update(tabe)
    # ---
    return named
