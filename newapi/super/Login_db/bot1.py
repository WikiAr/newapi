"""
Module for handling login attempt logging to database

from newapi.super.Login_db.bot import log_one

# log_one(site=f"{self.lang}.{self.family}.org", user=self.username, result=login_result)

"""
import sys
import json
import pymysql
import datetime

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'login_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def log_one(site="", user="", result=""):
    """
    Logs a login attempt to the database

    Args:
        site (str): The site where the login attempt occurred
        user (str): The username used in the attempt
        result (str): The result of the attempt (success/failure)
    """
    # ---
    timestamp = datetime.datetime.now().isoformat()
    # ---
    insert_query = """
        INSERT INTO login_attempts (site, username, result, timestamp)
        VALUES (%s, %s, %s, %s)
    """
    # ---
    try:
        connection = pymysql.connect(**DB_CONFIG)
        try:
            with connection.cursor() as cursor:
                cursor.execute(insert_query, (site, user, result, timestamp))
            connection.commit()
        except Exception as e:
            connection.rollback()
            print(f"Database error occurred: {e}")
        finally:
            connection.close()
    except pymysql.Error as e:
        print(f"Database error occurred: {e}")
