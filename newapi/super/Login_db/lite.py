"""
Module for handling login attempt logging to database

from newapi.super.Login_db.bot2 import log_one

# log_one(site="", user="", result="", db_type="sqlite", db_path="login_logs.db", credentials=None)

"""

import datetime
from pathlib import Path

from ...api_utils.except_err import exception_err
from ...DB_bots import db_bot

LiteDB = db_bot.LiteDB


def log_one_sqlite(site="", user="", result=""):
    Dir = Path(__file__).resolve().parent

    db_path = Dir / "login_logs.db"

    timestamp = datetime.datetime.now().isoformat()

    try:
        db = LiteDB(db_path)

        # Create table if it doesn't exist
        db.create_table(
            "login_attempts", {"id": int, "site": str, "username": str, "result": str, "timestamp": str}, pk="id"
        )

        # Insert login attempt
        db.insert(
            "login_attempts", {"site": site, "username": user, "result": result, "timestamp": timestamp}, check=False
        )  # Don't check for duplicates since each attempt should be logged

    except Exception as e:
        exception_err(e, "Failed to log login attempt to SQLite")
