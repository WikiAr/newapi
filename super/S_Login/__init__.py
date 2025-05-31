# -*- coding: utf-8 -*-
import os
if not os.getenv("BOTNAME"):
    botname = "newapi"

    if __file__.find("wikiapi_new") != -1:
        botname = "wikiapi_new"

    os.environ["BOTNAME"] = botname

    # os.getenv("BOTNAME")
