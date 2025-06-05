"""

python3 core8/pwb.py newapi/x_tests/test_login1 mwclient
python3 core8/pwb.py newapi/x_tests/test_login1

"""
import sys

sys.argv.append("printurl")
sys.argv.append("ask")
from newapi.super.S_Login import super_login

from newapi.accounts.useraccount import User_tables_bot

User_tables = User_tables_bot
User_tables["password"] += "123"
# ---

# super_login.User_tables["wikipedia"] = User_tables

Login = super_login.Login
# ---
bot = Login("simple", family="wikipedia")
login = bot.Log_to_wiki()
# ---
params = {"action": "query", "titles": "User:Mr. Ibrahem", "prop": "revisions", "rvprop": "content", "rvslots": "*", "format": "json"}
# ---
json1 = bot.post(params, Type="post", addtoken=False)
# ---
print(json1)

print(f"{len(json1)=}")
# ---
