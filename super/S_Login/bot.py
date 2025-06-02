"""

from .super.S_Login.bot import LOGIN_HELPS

Exception:{'login': {'result': 'Failed', 'reason': 'You have made too many recent login attempts. Please wait 5 minutes before trying again.'}}

"""
import sys
import os
import requests
from http.cookiejar import MozillaCookieJar

from ...api_utils import printe
from .cookies_bot import get_file_name, del_cookies_file
from ...api_utils.except_err import exception_err
from .params_help import PARAMS_HELPS
from ..Login_db.bot import log_one

# cookies = get_cookies(lang, family, username)
seasons_by_lang = {}
users_by_lang = {}
logins_count = {1: 0}
User_tables = {}

botname = "newapi"
if __file__.find("wikiapi_new") != -1:
    botname = "wikiapi_new"

def add_Usertables(table, family):
    User_tables[family] = table


def default_user_agent():
    tool = os.getenv("HOME")
    # "/data/project/mdwiki"
    tool = tool.split("/")[-1] if tool else "himo"
    # ---
    li = f"{tool} bot/1.0 (https://{tool}.toolforge.org/; tools.{tool}@toolforge.org)"
    # ---
    # printe.output(f"default_user_agent: {li}")
    # ---
    return li


# -----
# -----
# -----
# -----
# -----

class LOGIN_HELPS(PARAMS_HELPS):
    def __init__(self) -> None:
        # print("class LOGIN_HELPS:")
        self.cookie_jar = False
        self.session = requests.Session()
        # ---
        super().__init__()
        # ---
        # check if self has username before writeself.username = ""
        self.username = getattr(self, "username") if hasattr(self, "username") else ""
        self.family = getattr(self, "family") if hasattr(self, "family") else ""
        self.lang = getattr(self, "lang") if hasattr(self, "lang") else ""
        self.endpoint = getattr(self, "endpoint") if hasattr(self, "endpoint") else f"https://{self.lang}.{self.family}.org/w/api.php"
        # ---
        self.password = ""
        self.username_in = ""
        self.Bot_or_himo = 0
        self.cookies_file = ""
        self.user_table_done = False
        self.user_agent = default_user_agent()
        self.headers = {"User-Agent": self.user_agent}
        self.sea_key = f"{self.lang}-{self.family}-{self.username}"

    def log_error(self, result, action) -> None:
        log_one(site=f"{self.lang}.{self.family}.org", user=self.username, result=result, action=action)

    def add_User_tables(self, family, table) -> None:
        # ---
        if table["username"].find("bot") == -1 and family == "wikipedia":
            print(f"add_User_tables: {family=}, {table['username']=}")
        # ---
        if self.family == family or (self.lang == "ar" and self.family.startswith("wik")):  # wiktionary
            self.user_table_done = True
            # ---
            User_tables[family] = table
            # ---
            self.username = table["username"]
            self.password = table["password"]
            # ---
            self.sea_key = f"{self.lang}-{self.family}-{self.username}"

    def make_new_r3_token(self) -> str:
        # ---
        r3_params = {
            "format": "json",
            "action": "query",
            "meta": "tokens",
        }
        # ---
        req = self.post_it_parse_data(r3_params) or {}
        # ---
        if not req:
            return False

        csrftoken = req.get("query", {}).get("tokens", {}).get("csrftoken", "")
        # ---
        return csrftoken

    def log_in(self) -> bool:
        """
        Log in to the wiki and get authentication token.
        """
        # time.sleep(0.5)

        colors = {"ar": "yellow", "en": "lightpurple"}

        color = colors.get(self.lang, "")

        Bot_passwords = self.password.find("@") != -1
        logins_count[1] += 1
        printe.output(f"<<{color}>> {botname}/page.py: Log_to_wiki {self.endpoint} count:{logins_count[1]}")
        printe.output(f"{botname}/page.py: log to {self.lang}.{self.family}.org user:{self.username}, ({Bot_passwords=})")

        logintoken = self.get_logintoken()

        if not logintoken:
            return False

        success = self.get_login_result(logintoken)

        if success:
            printe.output("<<green>> new_api login Success")
            return True
        else:
            return False

    def get_logintoken(self) -> str:
        r1_params = {
            "format": "json",
            "action": "query",
            "meta": "tokens",
            "type": "login",
        }

        # WARNING: /data/project/himo/core/bots/{botname}/page.py:101: UserWarning: Exception:502 Server Error: Server Hangup for url: https://ar.wikipedia.org/w/api.php

        try:
            r11 = seasons_by_lang[self.sea_key].request("POST", self.endpoint, data=r1_params, headers=self.headers)
            # ---
            self.log_error(r11.status_code, "logintoken")
            # ---
            if not str(r11.status_code).startswith("2"):
                printe.output(f"<<red>> {botname} {r11.status_code} Server Error: Server Hangup for url: {self.endpoint}")
            # ---
        except Exception as e:
            exception_err(e)
            return ""

        jsson1 = {}

        try:
            jsson1 = r11.json()
        except Exception as e:
            print(r11.text)
            exception_err(e)
            return ""

        return jsson1.get("query", {}).get("tokens", {}).get("logintoken") or ""

    def get_login_result(self, logintoken) -> bool:
        if not self.password:
            printe.output("No password")
            return False

        r2_params = {
            "format": "json",
            "action": "login",
            "lgname": self.username,
            "lgpassword": self.password,
            "lgtoken": logintoken,
        }
        # ---
        req = ""
        # ---
        try:
            req = seasons_by_lang[self.sea_key].request("POST", self.endpoint, data=r2_params, headers=self.headers)
        except Exception as e:
            exception_err(e)
            return False
        # ---
        r22 = {}
        # ---
        if req:
            try:
                r22 = req.json()
            except Exception as e:
                exception_err(e)
                print(req.text)
                return False
        # ---
        login_result = r22.get("login", {}).get("result", "")
        # ---
        success = login_result.lower() == "success"
        # ---
        self.log_error(login_result, "login")
        # ---
        if success:
            self.loged_in()
            return True
        # ---
        reason = r22.get("login", {}).get("reason", "")
        # ---
        # exception_err(r22)
        # ---
        if reason == "Incorrect username or password entered. Please try again.":
            printe.output(f"user:{self.username}, pass:******")
        # ---
        return False

    def log_to_wiki_1(self, do=False) -> str:
        # ---
        return self.make_new_r3_token()

    def loged_in(self) -> bool:
        params = {
            "format": "json",
            "action": "query",
            "meta": "userinfo",
            "uiprop": "groups|rights",
        }
        # ---
        req = ""
        try:
            req = seasons_by_lang[self.sea_key].request("POST", self.endpoint, data=params, headers=self.headers)
        except Exception as e:
            exception_err(e)
            self.log_error("failed", "userinfo")
            return False
        # ---
        json1 = {}
        if req:
            try:
                json1 = req.json()
            except Exception as e:
                exception_err(e)
                print(req.text)
                return False
        # ---
        userinfo = json1.get("query", {}).get("userinfo", {})
        # ---
        result_x = "success" if userinfo else "failed"
        # ---
        self.log_error(result_x, "userinfo")
        # ---
        # print(json1)
        # ---
        if "anon" in userinfo or "temp" in userinfo:
            return False
        # ---
        self.username_in = userinfo.get("name", "")
        users_by_lang[self.lang] = self.username_in
        # ---
        return True

    def make_new_session(self) -> None:
        # ---
        print("make_new_session:")
        # ---
        seasons_by_lang[self.sea_key] = requests.Session()
        # ---
        self.cookies_file = get_file_name(self.lang, self.family, self.username)
        # ---
        self.cookie_jar = MozillaCookieJar(self.cookies_file)
        # ---
        if os.path.exists(self.cookies_file) and self.family != "mdwiki":
            print("Load cookies from file, including session cookies")
            try:
                self.cookie_jar.load(ignore_discard=True, ignore_expires=True)
                print("We have %d cookies" % len(self.cookie_jar))
                # ---
            except Exception as e:
                print(e)
        # ---
        seasons_by_lang[self.sea_key].cookies = self.cookie_jar
        # ---
        loged_t = False
        # ---
        if len(self.cookie_jar) > 0:
            if self.loged_in():
                loged_t = True
                printe.output("<<green>> Already logged in as " + self.username_in)
        else:
            loged_t = self.log_in()
        # ---
        if loged_t:
            self.cookie_jar.save(ignore_discard=True, ignore_expires=True)

    def _handle_server_error(self, req0, action):
        if req0 and req0.status_code:
            # ---
            self.log_error(req0.status_code, action)
            # ---
            if not str(req0.status_code).startswith("2"):
                printe.output(f"<<red>> {botname} {req0.status_code} Server Error: Server Hangup for url: {self.endpoint}")

    def raw_request(self, params, files=None, timeout=30) -> any or None:
        # ---
        # TODO: ('toomanyvalues', 'Too many values supplied for parameter "titles". The limit is 50.', 'See https://en.wikipedia.org/w/api.php for API usage. Subscribe to the mediawiki-api-announce mailing list at &lt;https://lists.wikimedia.org/postorius/lists/mediawiki-api-announce.lists.wikimedia.org/&gt; for notice of API deprecations and breaking changes.')
        # ---
        if not self.user_table_done:
            printe.output("<<green>> user_table_done == False!")
            printe.output("<<green>> user_table_done == False!")
            printe.output("<<green>> user_table_done == False!")
            # do error
            if "raise" in sys.argv:
                raise Exception("user_table_done == False!")
        # ---
        if self.family == "mdwiki":
            timeout = 60
        # ---
        args = {
            "files": files,
            "headers": self.headers,
            "data": params,
            "timeout": timeout,
        }
        # ---
        u_action = params.get("action", "")
        # ---
        if params.get('meta') == "tokens":
            u_action = "tokens"
            # ---
            if params.get('type'):
                u_action += "_" + params['type']
        # ---
        if "dopost" in sys.argv:
            printe.output("<<green>> dopost:::")
            printe.output(params)
            printe.output("<<green>> :::dopost")
            req0 = seasons_by_lang[self.sea_key].request("POST", self.endpoint, **args)
            # ---
            self._handle_server_error(req0, u_action)
            # ---
            return req0
        # ---
        req0 = None
        # ---
        try:
            req0 = seasons_by_lang[self.sea_key].request("POST", self.endpoint, **args)

        except requests.exceptions.ReadTimeout:
            self.log_error("ReadTimeout", u_action)
            printe.output(f"<<red>> ReadTimeout: {self.endpoint=}, {timeout=}")

        except Exception as e:
            self.log_error("Exception", u_action)
            exception_err(e)
        # ---
        self._handle_server_error(req0, u_action)
        # ---
        return req0

    def post_it(self, params, files=None, timeout=30) -> any or None:
        # ---
        params = self.params_w(params)
        # ---
        session = seasons_by_lang.get(self.sea_key)
        # ---
        if not self.username_in:
            self.username_in = users_by_lang.get(self.lang, "")
        # ---
        if not session:
            self.make_new_session()
        # ---
        if not self.username_in:
            printe.output("<<red>> no username_in.. action:" + params.get("action"))
            # return {}
        # ---
        req0 = self.raw_request(params, files=files, timeout=timeout)
        # ---
        if not req0:
            printe.output("<<red>> no req0.. ")
            return req0
        # ---
        if req0.headers and req0.headers.get("x-database-lag"):
            printe.output("<<red>> x-database-lag.. ")
            print(req0.headers)
            # raise
        # ---
        return req0

    def post_it_parse_data(self, params, files=None, timeout=30, relogin=False) -> dict:
        # ---
        req = self.post_it(params, files, timeout)
        # ---
        data = {}
        # ---
        if req:
            data = self.parse_data(req) or {}
        # ---
        error = data.get("error", {})
        # ---
        # {'code': 'assertnameduserfailed', 'info': 'You are no longer logged in as "Mr. Ibrahem", ....', '*': ''}
        # ---
        if error:
            code = error.get("code", "")
            # ---
            if code == "assertnameduserfailed":
                # ---
                print("assertnameduserfailed" * 10)
                # ---
                del_cookies_file(self.cookies_file)
                # ---
                self.username_in = ""
                self.make_new_session()
                # ---
                return self.post_it_parse_data(params, files, timeout, relogin=True)
        # ---
        return data

    def get_rest_result(self, url) -> dict:
        # ---
        print("get_rest_result:")
        # ---
        result = {}
        # ---
        try:
            req0 = seasons_by_lang[self.sea_key].request("GET", url)
            result = req0.json()

        except Exception as e:
            exception_err(e)
        # ---
        return result
