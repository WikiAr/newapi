"""
Module for handling login attempt logging to database

from newapi.super.Login_db.bot2 import log_one

# log_one(site="", user="", result="", db_type="sqlite", db_path="login_logs.db", credentials=None)

"""
import os
import datetime
from configparser import ConfigParser
from ...api_utils import printe
from ...DB_bots.pymysql_bot import sql_connect_pymysql

def local_host():
    main_args = {
        "host": "127.0.0.1",
        "db": "mv",
        "charset": "utf8mb4",
        # "cursorclass": Typee,
        "use_unicode": True,
        "autocommit": True,
    }

    credentials = {"user": "root", "password": "root11"}

    return main_args, credentials

def jls_extract_def():
    # ---
    if not os.getenv("HOME"):
        return local_host()
    # ---
    project = os.getenv("HOME")
    # ---
    if __file__.find('/data/project/himo') != -1:
        project = "/data/project/himo"
    # ---
    db_connect_file = f"{project}/confs/db.ini"
    db_username = ""
    credentials = {"read_default_file": db_connect_file}
    # ---
    # if db_connect_file is not file
    if os.path.isfile(db_connect_file):
        # ---
        try:
            config2 = ConfigParser()
            config2.read(db_connect_file)
            db_username = config2["client"]["user"]
        except KeyError as e:
            print(f"error: {e}")
    # ---
    # Typee = pymysql.cursors.DictCursor if return_dict else pymysql.cursors.Cursor
    # ---
    main_args = {
        "host": "tools.db.svc.wikimedia.cloud",
        "db": f"{db_username}__mv",
        "charset": "utf8mb4",
        # "cursorclass": Typee,
        "use_unicode": True,
        "autocommit": True,
    }

    if os.getenv("HOME").find("/data/project/mdwiki") != -1:
        main_args["db"] = f"{db_username}__mdwiki_new"

    return main_args, credentials


main_args, credentials = jls_extract_def()

userinfo = 0

def log_one(site, user, result, action="", params={}):
    # global userinfo
    # ---
    params = params or {}
    # ---
    if params.get('meta', "") == "tokens":
        action = "tokens"
        if params.get('type'):
            action += "_" + params['type']
    elif params.get('meta', "").find("userinfo") != -1:
        action = "userinfo"
    # ---
    # if params.get('meta', "").find("userinfo") != -1:
    #     userinfo += 1
    #     if userinfo > 3:
    #         raise Exception("too much")
    # ---
    if action == "query" and params.get('prop'):
        action += "_" + "_".join(params['prop'].split("|"))
    # ---
    if action == "query":
        printe.output(f"<<yellow>> {action=}")
        print(dict(params))
    # ---
    # Create table query
    _create_table_query = """
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            site VARCHAR(255) NOT NULL,
            username VARCHAR(255) NOT NULL,
            result VARCHAR(50) NOT NULL,
            timestamp DATETIME NOT NULL,
            action VARCHAR(100) NULL,
            INDEX idx_site_user (site, username),
            INDEX idx_timestamp (timestamp)
        )
        """
    # Create table query
    create_table_query = """
        CREATE TABLE IF NOT EXISTS `logins` (
            `id` int NOT NULL AUTO_INCREMENT,
            `site` varchar(255) NOT NULL,
            `username` varchar(255) NOT NULL,
            `result` varchar(50) NOT NULL,
            `action` varchar(100) DEFAULT NULL,
            `count` int NOT NULL DEFAULT '1',
            `first` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `last` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`),
            UNIQUE KEY `site_username_result_action` (`site`,`username`,`result`,`action`),
            KEY `idx_site_user` (`site`,`username`),
            KEY `idx_timestamp` (`first`)
        )
    """
    # print(f"create_table_query: {create_table_query}")

    timestamp = datetime.datetime.now().isoformat()

    # Execute table creation
    sql_connect_pymysql(
        create_table_query,
        main_args=main_args,
        credentials=credentials
        )

    # Insert login attempt
    insert_query = """
        INSERT INTO logins (site, username, result, action, count, first, last)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        ON DUPLICATE KEY UPDATE count = count + 1, last = NOW()
    """

    # print(f"insert_query: {insert_query}")

    sql_connect_pymysql(
        insert_query,
        values=(site, user, result, action, 1),
        main_args=main_args,
        credentials=credentials,
    )
