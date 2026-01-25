"""

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

User_tables = {
    "username": my_username,
    "password": mdwiki_pass,
}

User_tables_wiki = {
    "username": bot_username,
    "password": bot_password,
}

SITECODE = "www"
FAMILY = "mdwiki"
