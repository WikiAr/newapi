"""

python3 core8/pwb.py newapi/x_tests/test_login mwclient
python3 core8/pwb.py newapi/x_tests/test_login
"""
import sys

sys.argv.append("printurl")
sys.argv.append("ask")
from newapi.accounts import useraccount
from newapi.super.S_Login import super_login

User_tables = {"username": useraccount.username, "password": useraccount.password}
# ---

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
