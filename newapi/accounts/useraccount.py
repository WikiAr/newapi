"""

from newapi.accounts.useraccount import User_tables_bot, User_tables_ibrahem

"""
import sys
import os
import configparser

project = '/data/project/himo'
# ---
if not os.path.isdir(project):
    project = 'I:/core/bots/core1'
# ---
config = configparser.ConfigParser()
config.read(f"{project}/confs/user.ini")

DEFAULT = config['DEFAULT']

username = config['DEFAULT'].get('botusername', "")
password = config['DEFAULT'].get('botpassword', "")
# ---

passworden = config['DEFAULT'].get('passworden', "")
passwordwd = config['DEFAULT'].get('passwordwd', "")

password_ar = config['DEFAULT'].get('password_ar', "")
password_en = config['DEFAULT'].get('password_en', "")

hiacc = config['DEFAULT'].get('hiacc', "")
hipass = config['DEFAULT'].get('hipass', "")

mdwiki_pass = config['DEFAULT'].get('mdwiki_pass', "")

qs_token = config['DEFAULT'].get('qs_token', "")
qs_tokenbot = config['DEFAULT'].get('qs_tokenbot', "")

user_agent = config['DEFAULT'].get('user_agent', "")

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
