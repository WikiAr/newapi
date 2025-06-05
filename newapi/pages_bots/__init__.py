# -*- coding: utf-8 -*-
import os
if not os.getenv("BOTNAME"):
    botname = "newapi"
    os.environ["BOTNAME"] = botname

    # os.getenv("BOTNAME")
