"""

python3 core8/pwb.py newapi/tests/test_login nomwclient

python3 core8/pwb.py newapi/tests/test_login

"""
from newapi import useraccount

User_tables = {"username": useraccount.username, "password": useraccount.password}
# ---
from newapi.super.S_Login import super_login

Login = super_login.Login
# ---
bot = Login("ar", family="wikipedia")
# ---
bot.add_User_tables("wikipedia", User_tables)
# ---
params = {"action": "query", "titles": f"User:{User_tables['username']}", "prop": "revisions", "rvprop": "content", "rvslots": "*", "format": "json"}
# ---
json1 = bot.post(params, Type="post", addtoken=False)
# ---
# print(json1)

print(f"{len(json1)=}")
