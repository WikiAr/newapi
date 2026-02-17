"""

from .super.cookies_bot import get_cookies
# cookies = get_cookies(lang, family, username)

"""

import logging
import os
import stat
import sys
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

statgroup = stat.S_IRWXU | stat.S_IRWXG
tool = os.getenv("HOME")
# ---
if not tool:
    tool = Path(__file__).parent
else:
    tool = Path(tool)
# ---
ta_dir = tool / "cookies"
# ---
if not ta_dir.exists():
    ta_dir.mkdir()
    logger.info("<<green>> mkdir:")
    logger.info(f"ta_dir:{ta_dir}")
    logger.info("<<green>> mkdir:")
    os.chmod(ta_dir, statgroup)


def del_cookies_file(file_path):
    # ---
    file = Path(str(file_path))
    # ---
    if file.exists():
        try:
            file.unlink(missing_ok=True)
            logger.info(f"<<green>> unlink: file:{file}")
        except Exception as e:
            logger.error(f"<<red>> unlink: Exception:{e}")


def get_file_name(lang, family, username) -> Path:
    # ---
    if "nocookies" in sys.argv:
        randome = os.urandom(8).hex()
        return ta_dir / f"{randome}.txt"
    # ---
    lang = lang.lower()
    family = family.lower()
    # ---
    username = username.lower().replace(" ", "_").split("@")[0]
    # ---
    file = ta_dir / f"{family}_{lang}_{username}.txt"
    # ---
    if file.exists():
        # ---
        # check if file old is > 3 days
        # ---
        file_time = datetime.fromtimestamp(file.stat().st_mtime)
        # ---
        if not file.stat().st_size:
            del_cookies_file(file)
        elif datetime.now() - file_time > timedelta(days=3):
            del_cookies_file(file)
        # ---
    return file


def from_folder(lang, family, username):
    # ---
    file = get_file_name(lang, family, username)
    # ---
    cookies = False
    # ---
    if file.exists():
        # ---
        if not file.stat().st_size:
            return False
        # ---
        # check if file old is > 3 days
        # ---
        file_time = datetime.fromtimestamp(file.stat().st_mtime)
        # ---
        if datetime.now() - file_time > timedelta(days=3):
            del_cookies_file(file)
            return False
        # ---
        with open(file, "r", encoding="utf-8") as f:
            cookies = f.read()
    else:
        file.touch()
        os.chmod(str(file), statgroup)
    # ---
    return cookies


@lru_cache(maxsize=128)
def get_cookies(lang, family, username):
    # ---
    cookies = from_folder(lang, family, username)
    # ---
    if not cookies:
        logger.info(f" <<red>> get_cookies: <<yellow>> [[{lang}:{family}]] user:{username} <<red>> not found")
        return "make_new"
    # ---
    return cookies
