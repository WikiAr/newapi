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
