"""

python3 core8/pwb.py newapi/tests/test_login1 nomwclient
python3 core8/pwb.py newapi/tests/test_login1

wikiapi_new:
python3 core8/pwb.py newapi/tests/test_login1 wikiapi_new nomwclient
python3 core8/pwb.py newapi/tests/test_login1 wikiapi_new

"""
import sys

sys.argv.append("printurl")
sys.argv.append("ask")

if "wikiapi_new" in sys.argv:
    from wikiapi_new.accounts import useraccount
    from wikiapi_new.super.S_Login import super_login
else:
    from newapi.accounts import useraccount
    from newapi.super.S_Login import super_login

User_tables = {"username": useraccount.username, "password": f"{useraccount.password}213"}
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
