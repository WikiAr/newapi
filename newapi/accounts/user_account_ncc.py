"""
# ---
from .accounts import user_account_ncc
# ---
User_tables = {
    "username": user_account_ncc.username,
    "password": user_account_ncc.password,
}
# ---
"""

import configparser
import os

home_dir = os.getenv("HOME")
project = home_dir if home_dir else "I:/ncc"
# ---
config = configparser.ConfigParser()
config.read(f"{project}/confs/nccommons_user.ini")
# ---
username = config["DEFAULT"].get("username", "").strip()
password = config["DEFAULT"].get("password", "").strip()

User_tables = {
    "username": username,
    "password": password,
}

SITECODE = "www"
FAMILY = "nccommons"
