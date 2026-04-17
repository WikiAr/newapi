""" """

import os
import sys

qs_token = os.getenv("QS_TOKEN", "")
qs_tokenbot = os.getenv("QS_TOKEN_BOT", "")

user_agent = "Himo Bot/1.0 (https://himo.toolforge.org/; tools.himo@toolforge.org)"

username = os.getenv("WIKIPEDIA_BOT_USERNAME", "")
password = os.getenv("WIKIPEDIA_BOT_PASSWORD", "")

hiacc = os.getenv("WIKIPEDIA_HIMO_USERNAME", "")
hipass = os.getenv("WIKIPEDIA_HIMO_PASSWORD", "")

if "workibrahem" in sys.argv:
    username = hiacc
    password = hipass

User_tables_bot = {
    "username": str(username),
    "password": str(password),
}
# ---
User_tables_ibrahem = {
    "username": hiacc,
    "password": hipass,
}

__all__ = [
    "home_dir",
    "user_agent",
    "MainPage",
    "NEW_API",
    "CatDepth",
    "change_codes",
]
