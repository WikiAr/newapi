"""
Test runner usage: python3 core8/pwb.py newapi_bot/z_te_sts/test_runner
"""

import sys

sys.argv.append("printurl")
sys.argv.append("ask")
from newapi.accounts.useraccount import User_tables_bot
from newapi.super import super_login

User_tables = User_tables_bot
# ---

Login = super_login.Login
# ---
bot = Login("ar", family="wikipedia")
# ---
bot.add_User_tables("wikipedia", User_tables)
# ---
params = {
    "action": "query",
    "titles": f"User:{User_tables['username']}",
    "prop": "revisions",
    "rvprop": "content",
    "rvslots": "*",
    "format": "json",
}
# ---
json1 = bot.post(params, Type="post", addtoken=False)
# ---
# print(json1)

print(f"{len(json1)=}")
