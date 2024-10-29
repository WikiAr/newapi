"""

from newapi.super.login_bots.bot_new import LOGIN_HELPS

Exception:{'login': {'result': 'Failed', 'reason': 'You have made too many recent login attempts. Please wait 5 minutes before trying again.'}}

"""
import sys
import os

# import json
import requests
from http.cookiejar import MozillaCookieJar

from newapi import printe
from newapi.super.login_bots.cookies_bot import get_file_name, del_cookies_file
from newapi.except_err import exception_err
from newapi.super.login_bots.params_help import PARAMS_HELPS

# import mwclient

# from mwclient.client import Site
from newapi.super.login_bots.mwclient.client import Site

# cookies = get_cookies(lang, family, username)
users_by_lang = {}
User_tables = {}
logins_count = {1: 0}


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


class MwClientSite:
    def __init__(self, lang, family):
        self.lang = lang
        self.family = family
        self.username = None
        self.password = None
        self.force_login = "nologin" not in sys.argv
        self.user_agent = default_user_agent()

        self.site_mwclient = None
        # self._start_()

    def _start_(self, username, password):
        self.username = username
        self.password = password

        self.__initialize_connection()
        self.__initialize_site()
        self.do_login()

    def __initialize_connection(self):
        """Initialize a connection with session cookies.

        This method sets up a requests session with a specified user agent and
        attempts to load cookies from a file if it exists. The cookies are used
        to maintain the session state across requests. If the cookies file is
        not found or an error occurs while loading the cookies, an error message
        is printed to the output.
        """

        cookies_file = get_file_name(self.lang, self.family, self.username)

        self.jar_cookie = MozillaCookieJar(cookies_file)

        self.connection = requests.Session()

        self.connection.headers["User-Agent"] = default_user_agent()

        if os.path.exists(cookies_file) and self.family != "mdwiki":
            # printe.output("<<yellow>>loading cookies")
            try:
                # Load cookies from file, including session cookies
                self.jar_cookie.load(ignore_discard=True, ignore_expires=True)
                self.connection.cookies = self.jar_cookie  # Tell Requests session to use the cookiejar.
            except Exception as e:
                printe.output("Could not load cookies: %s" % e)

    def __initialize_site(self):
        """Initialize the site with the specified domain and client settings.

        This method constructs the domain using the language and family
        attributes, then attempts to create a MediaWiki client instance. If the
        "dopost" argument is present in the command line arguments, it
        initializes the client accordingly. If an exception occurs during the
        client initialization, it logs an error message and returns False.

        Returns:
            bool: Returns False if the client could not be initialized due to an error.
        """

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
        """Perform the login process for the user.

        This method checks if a forced login is required and if the MediaWiki
        client is available. If the client is not logged in, it attempts to log
        in using the provided username and password. Upon successful login, it
        saves the session cookies to a file. If any errors occur during the
        login attempt, an error message is printed.
        """

        if not self.force_login:
            return

        if not self.site_mwclient:
            printe.output(f"no self.ssite_mwclient to ({self.domain})")
            return

        if not self.site_mwclient.logged_in:
            logins_count[1] += 1
            printe.output(f"<<yellow>>logging in to ({self.domain}) count:{logins_count[1]}")
            try:
                self.site_mwclient.login(username=self.username, password=self.password)
            except Exception as e:
                printe.output(f"Could not login to ({self.domain}): %s" % e)

            if self.site_mwclient.logged_in:
                printe.output(f"<<purple>>logged in as {self.site_mwclient.username} to ({self.domain})")

            # Save cookies to file, including session cookies
            self.jar_cookie.save(ignore_discard=True, ignore_expires=True)

    def do_request(self, params=None, method="POST"):
        # ---
        params = params.copy()
        # ---
        action = params["action"]
        # ---
        del params["action"]
        # ---
        if "dopost" in sys.argv:
            r4 = self.site_mwclient.api(action, http_method=method, **params)
            return r4
        else:
            try:
                r4 = self.site_mwclient.api(action, http_method=method, **params)
                return r4

            except Exception as e:
                exception_err(e, text=params)
        # ---
        return {}


class LOGIN_HELPS(MwClientSite, PARAMS_HELPS):
    def __init__(self) -> None:
        # ---
        self.family = getattr(self, "family") if hasattr(self, "family") else ""
        self.lang = getattr(self, "lang") if hasattr(self, "lang") else ""
        # ---
        super().__init__(self.lang, self.family)
        # ---
        self.username = ""
        self.password = ""
        self.username_in = ""
        self.Bot_or_himo = 0
        self.user_table_done = False

    def add_User_tables(self, family, table) -> None:
        # print(f"add_User_tables: {family=}")
        if self.family == family:
            self.user_table_done = True
            User_tables[family] = table
            self.username = table["username"]
            self.password = table["password"]
            self._start_(self.username, self.password)

    def make_new_r3_token(self) -> str:
        """Retrieve a new CSRF token from the site.

        This function attempts to obtain a CSRF token using the site's mediawiki
        client. If successful, it returns the token as a string. If there is an
        error during the token retrieval process, it logs the error message and
        returns False.

        Returns:
            str: The CSRF token if successful, otherwise False.
        """

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

    def post_it_2(self, params, files=None, timeout=30) -> any or None:
        """Send a POST request to a specified endpoint with given parameters and
        files.

        This method constructs a POST request using the provided parameters and
        optional files. It includes error handling for various scenarios, such
        as checking if the user table is ready and managing request timeouts. If
        the request is successful, it returns the response object.

        Args:
            params (dict): A dictionary of parameters to include in the POST request.
            files (dict?): A dictionary of files to upload with the request. Defaults to None.
            timeout (int?): The timeout for the request in seconds. Defaults to 30.

        Returns:
            any or None: The response object from the POST request, or None if the
                request fails.

        Raises:
            Exception: If the user table is not ready when attempting to send the request.
            requests.exceptions.ReadTimeout: If the request times out.
        """
        # ---
        if not self.user_table_done:
            printe.output("<<green>> user_table_done == False!")
            printe.output("<<green>> user_table_done == False!")
            printe.output("<<green>> user_table_done == False!")
            # do error
            if "raise" in sys.argv:
                raise Exception("user_table_done == False!")
        # ---
        req0 = self.do_request(params=params, method="POST")
        # ---
        return req0

    def post_it(self, params, files=None, timeout=30) -> any or None:
        # ---
        params = self.params_w(params)
        # ---
        req0 = self.post_it_2(params, files=files, timeout=timeout)
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
