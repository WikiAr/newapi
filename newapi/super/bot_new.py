"""

from .super.bot_new import LOGIN_HELPS

Exception:{'login': {'result': 'Failed', 'reason': 'You have made too many recent login attempts. Please wait 5 minutes before trying again.'}}

"""
import sys
import os
import copy
import requests
from http.cookiejar import MozillaCookieJar

from ..api_utils import printe
from ..api_utils.except_err import exception_err
from .cookies_bot import get_file_name, del_cookies_file

from .params_help import PARAMS_HELPS
from .Login_db.bot import log_one
from ..api_utils.user_agent import default_user_agent
# import mwclient

# from mwclient.client import Site
from .mwclient.client import Site

# cookies = get_cookies(lang, family, username)
logins_count = {1: 0}


class MwClientSite:
    def __init__(self, lang, family):
        self.lang = lang
        self.family = family
        self.username = getattr(self, "username", None)
        self.password = None
        # ---
        self.login_done = False
        # ---
        self.force_login = "nologin" not in sys.argv
        self.user_agent = default_user_agent()
        self.domain = getattr(self, "domain", "")

        self.site_mwclient = None
        self.jar_cookie = None
        self.connection = None
        # self._start_()

    def log_error(self, result, action, params=None) -> None:
        log_one(site=f"{self.lang}.{self.family}.org", user=self.username, result=result, action=action, params=params)

    def _start_(self, username, password):
        self.username = username
        self.password = password

        self.__initialize_connection()
        self.__initialize_site()
        self.do_login()

    def __initialize_connection(self):
        cookies_file = get_file_name(self.lang, self.family, self.username)

        self.jar_cookie = MozillaCookieJar(cookies_file)

        self.connection = requests.Session()

        self.connection.headers["User-Agent"] = default_user_agent()
        # ---
        if os.path.exists(cookies_file) and self.family != "mdwiki":
            # printe.output("<<yellow>>loading cookies")
            try:
                # Load cookies from file, including session cookies
                self.jar_cookie.load(ignore_discard=True, ignore_expires=True)
                self.connection.cookies = self.jar_cookie  # Tell Requests session to use the cookiejar.
            except Exception as e:
                printe.output("Could not load cookies: %s" % e)

    def __initialize_site(self):
        self.domain = f"{self.lang}.{self.family}.org"

        if "dopost" in sys.argv:
            self.site_mwclient = Site(self.domain, clients_useragent=self.user_agent, pool=self.connection, force_login=self.force_login)
        else:
            try:
                self.site_mwclient = Site(self.domain, clients_useragent=self.user_agent, pool=self.connection, force_login=self.force_login)
            except Exception as e:
                printe.output(f"Could not connect to ({self.domain}): %s" % e)
                return False

    def do_login(self):

        if not self.force_login:
            printe.output("<<red>> do_login(): not self.force_login ")
            return

        if not self.site_mwclient:
            printe.output(f"no self.ssite_mwclient to ({self.domain})")
            return

        if not self.site_mwclient.logged_in:
            logins_count[1] += 1
            printe.output(f"<<yellow>>logging in to ({self.domain}) count:{logins_count[1]}, user: {self.username}")
            # ---
            try:
                login_result = self.site_mwclient.login(username=self.username, password=self.password)

                self.log_error(login_result, "login")
                self.login_done = True

            except Exception as e:
                printe.output(f"Could not login to ({self.domain}): %s" % e)

            if self.site_mwclient.logged_in:
                printe.output(f"<<purple>>logged in as {self.site_mwclient.username} to ({self.domain})")

            # Save cookies to file, including session cookies
            if self.jar_cookie:
                self.jar_cookie.save(ignore_discard=True, ignore_expires=True)

    def do_request(self, params=None, method="POST"):
        # ---
        if not self.login_done:
            self.do_login()
        # ---
        params = copy.deepcopy(params)
        # ---
        action = params["action"]
        # ---
        del params["action"]
        # ---
        if not self.site_mwclient:
            printe.output(f"no self.ssite_mwclient to ({self.domain})")
            self.__initialize_site()
            self.do_login()
        # ---
        if "dopost" in sys.argv:
            r4 = self.site_mwclient.api(action, http_method=method, **params)
            return r4
        # ---
        try:
            r4 = self.site_mwclient.api(action, http_method=method, **params)
            # ---
            # self.log_error("success", action)
            # ---
            return r4

        except Exception as e:
            # ---
            self.log_error("Exception", action, params=params)
            # ---
            if "text" in params:
                params["text"] = params["text"][:100]
            # ---
            exception_err(e, text=params)
        # ---
        return {}


# -----
# -----
# -----
# -----
# -----

class LOGIN_HELPS(MwClientSite, PARAMS_HELPS):
    def __init__(self) -> None:
        # ---
        self.family = getattr(self, "family", "")
        self.lang = getattr(self, "lang", "")
        # ---
        self.cookies_file = getattr(self, "cookies_file", "")
        # ---
        self.username = getattr(self, "username", "")
        self.password = ""
        self.username_in = ""
        self.Bot_or_himo = 0
        self.user_table_done = False
        # ---
        super().__init__(self.lang, self.family)

    def add_User_tables(self, family, table, lang="") -> None:
        # ---
        langx = self.lang
        # ---
        # for example family=toolforge, lang in (medwiki, mdwikicx)
        if lang and not self.family.startswith("wik"):
            langx = lang
        # ---
        if table["username"].find("bot") == -1 and family == "wikipedia":
            print(f"add_User_tables: {family=}, {table['username']=}")
        # ---
        if family != "" and table['username'] != "" and table['password'] != "":
            # ---
            if self.family == family or (langx == "ar" and self.family.startswith("wik")):  # wiktionary
                self.user_table_done = True
                # ---
                self.username = table["username"]
                self.password = table["password"]
                # ---
                self._start_(self.username, self.password)

    def make_new_r3_token(self) -> str:
        # ---
        try:
            csrftoken = self.site_mwclient.get_token("csrf")
        except Exception as e:
            printe.output("Could not get token: %s" % e)
            return False
        # ---
        return csrftoken

    def log_to_wiki_1(self, do=False) -> str:
        # ---
        return self.make_new_r3_token()

    def raw_request(self, params, files=None, timeout=30):
        # ---
        if not self.user_table_done:
            printe.output("<<green>> user_table_done == False!")
            # do error
            if "raise" in sys.argv:
                raise Exception("user_table_done == False!")
        # ---
        req0 = self.do_request(params=params, method="POST")
        # ---
        return req0

    def post_it(self, params, files=None, timeout=30):
        # ---
        params = self.params_w(params)
        # ---
        req0 = self.raw_request(params, files=files, timeout=timeout)
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
                del_cookies_file(self.cookies_file)
                # ---
                self.username_in = ""
                self._start_(self.username, self.password)
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
            req0 = self.connection.request("GET", url)
            result = req0.json()

        except Exception as e:
            exception_err(e)
        # ---
        return result

    def make_new_session(self) -> None:
        return None
