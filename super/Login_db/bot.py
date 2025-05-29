"""
Module for handling login attempt logging to database

from newapi.super.Login_db.bot2 import log_one

# log_one(site="", user="", result="", db_type="sqlite", db_path="login_logs.db", credentials=None)

"""
import os
from newapi.pymysql_bot import sql_connect_pymysql
import datetime
from configparser import ConfigParser


if os.getenv("HOME"):
    project = "/data/project/himo"
else:
    project = 'I:/core/bots/core1'

db_connect_file = f"{project}/confs/db.ini"
db_username = ""
credentials = {}

# if db_connect_file is not file
if os.path.isfile(db_connect_file):
    credentials = {"read_default_file": db_connect_file}
    config2 = ConfigParser()
    config2.read(db_connect_file)
    # ---
    try:
        db_username = config2["client"]["user"]
    except KeyError as e:
        print(f"error: {e}")
# ---
# Typee = pymysql.cursors.DictCursor if return_dict else pymysql.cursors.Cursor

main_args = {
    "host": "tools.db.svc.wikimedia.cloud",
    "db": f"{db_username}__mv",
    "charset": "utf8mb4",
    # "cursorclass": Typee,
    "use_unicode": True,
    "autocommit": True,
}

if not os.getenv("HOME"):
    credentials = {"user": "root", "password": "root11"}
    main_args["host"] = "127.0.0.1"
    main_args["db"] = "mv"

elif os.getenv("HOME") == "/data/project/mdwiki":
    main_args["db"] = "s54732__mdwiki_new"

def log_one(site, user, result):

    timestamp = datetime.datetime.now().isoformat()

    # Create table query
    create_table_query = """
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            site VARCHAR(255) NOT NULL,
            username VARCHAR(255) NOT NULL,
            result VARCHAR(50) NOT NULL,
            timestamp DATETIME NOT NULL,
            INDEX idx_site_user (site, username),
            INDEX idx_timestamp (timestamp)
        )
    """
    print(f"create_table_query: {create_table_query}")

    # Execute table creation
    sql_connect_pymysql(
        create_table_query,
        main_args=main_args,
        credentials=credentials
        )

    # Insert login attempt
    insert_query = """
        INSERT INTO login_attempts (site, username, result, timestamp)
        VALUES (%s, %s, %s, %s)
    """

    print(f"insert_query: {insert_query}")

    sql_connect_pymysql(
        insert_query,
        values=(site, user, result, timestamp),
        main_args=main_args,
        credentials=credentials,
    )
