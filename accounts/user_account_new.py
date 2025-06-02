"""
# ---
from . import user_account_new
# ---
username = user_account_new.bot_username     #user_account_new.my_username
password = user_account_new.bot_password     #user_account_new.mdwiki_pass
lgpass_enwiki   = user_account_new.lgpass_enwiki
user_agent   = user_account_new.user_agent
# ---
"""

import os
import configparser

home_dir = os.getenv("HOME")
project = home_dir if home_dir else "I:/mdwiki/mdwiki"
# ---
config = configparser.ConfigParser()
config.read(f"{project}/confs/user.ini")

username = config["DEFAULT"].get("botusername", "")
password = config["DEFAULT"].get("botpassword", "")

bot_username = config["DEFAULT"].get("botusername", "")
bot_password = config["DEFAULT"].get("botpassword", "")

my_username = config["DEFAULT"].get("my_username", "")

mdwiki_pass = config["DEFAULT"].get("mdwiki_pass", "")

lgpass_enwiki = config["DEFAULT"].get("lgpass_enwiki", "")
my_password = lgpass_enwiki

qs_token = config["DEFAULT"].get("qs_token", "")

user_agent = config["DEFAULT"].get("user_agent", "")
