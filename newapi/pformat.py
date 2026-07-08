""" """

import wikitextparser as wtp


def make_new_text(text: str):
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
