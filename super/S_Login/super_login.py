# ---
"""
from newapi.super.S_Login import super_login
# ---
# bot   = Login(lang, family="wikipedia")
# login = bot.Log_to_wiki()
# json1 = bot.post_params(params, Type="post", addtoken=False, files=None)

# ----

Exception:{'login': {'result': 'Failed', 'reason': 'You have made too many recent login attempts. Please wait 5 minutes before trying again.'}}

# ----

"""
import os
import copy
import sys
import time
import urllib.parse

from newapi import printe
from newapi.super.handel_errors import HANDEL_ERRORS
from newapi.except_err import warn_err

if "nomwclient" in sys.argv:
    from newapi.super.S_Login.bot import LOGIN_HELPS
else:
    from newapi.super.S_Login.bot_new import LOGIN_HELPS

file_name = os.path.basename(__file__)
print_test = {1: False}
User_tables = {"mdwiki": {}, "wikidata": {}, "wikipedia": {}, "nccommons": {}}
seasons_by_lang = {}
ar_lag = {1: 3}


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


def test_print(s):
    if "test_print" in sys.argv:
        printe.output(s)


class Login(LOGIN_HELPS, HANDEL_ERRORS):
    """
    Represents a login session for a wiki.
    """

    def __init__(self, lang, family="wikipedia"):
        # print(f"class Login:{lang=}")

        super().__init__()

        self.lang = lang
        self.family = family
        self.r3_token = ""
        self.url_o_print = ""
        self.user_agent = default_user_agent()
        # self.headers = {"User-Agent": self.user_agent}

        self.endpoint = f"https://{self.lang}.{self.family}.org/w/api.php"

    def Log_to_wiki(self):
        """
        Log in to the wiki.
        """
        return True

    def p_url(self, params):
        """
        Print the URL for debugging purposes.
        """
        if print_test[1] or "printurl" in sys.argv:
            no_url = ["lgpassword", "format"]
            no_remove = ["titles", "title"]
            pams2 = {k: v[:100] if isinstance(v, str) and len(v) > 100 and k not in no_remove else v for k, v in params.items() if k not in no_url}
            self.url_o_print = f"{self.endpoint}?{urllib.parse.urlencode(pams2)}".replace("&format=json", "")
            printe.output(self.url_o_print)

    def make_response(self, params, files=None, timeout=30, do_error=True):
        """
        Make a POST request to the API endpoint.
        """
        self.p_url(params)

        data = {}

        if params.get("list") == "querypage":
            timeout = 60
        # ---
        req = self.post_it(params, files, timeout)
        # ---
        if req:
            data = self.parse_data(req)
        # ---
        # assertnameduserfailed
        # ---
        error = data.get("error", {})
        if error != {}:
            # print(data)
            er = self.handel_err(error, "", params=params, do_error=do_error)
            # ---
            if do_error:
                return er
        # ---
        return data

    def filter_params(self, params):
        """
        Filter out unnecessary parameters.
        """
        if self.family == "nccommons" and params.get("bot"):
            del params["bot"]

        if "workibrahem" in sys.argv and "ibrahemsummary" not in sys.argv and params.get("summary", "").find("بوت:") != -1:
            params["summary"] = ""

        if params["action"] in ["query"]:
            if "bot" in params:
                del params["bot"]
            if "summary" in params:
                del params["summary"]

        return params

    def post(self, params, Type="get", addtoken=False, CSRF=True, files=None):
        return self.post_params(params, Type=Type, addtoken=addtoken, CSRF=CSRF, files=files)

    def post_params(self, params, Type="get", addtoken=False, CSRF=True, files=None, do_error=False, max_retry=0):
        """
        Make a POST request to the API endpoint with authentication token.
        """
        params["format"] = "json"
        params["utf8"] = 1
        # ---
        wb_actions = [
            "wbcreateclaim",
            "wbcreateredirect",
            "wbeditentity",
            "wbmergeitems",
            "wbremoveclaims",
            "wbsetaliases",
            "wbsetdescription",
            "wbsetqualifier",
            "wbsetsitelink",
            "edit",
        ]
        # ---
        action = params["action"]
        # ---
        to_add_action = action in wb_actions or action.startswith("wbcreate") or action.startswith("wbset")
        # ---
        if self.family == "wikidata" and to_add_action:
            params["maxlag"] = ar_lag[1]

        # if addtoken or params["action"] in ["edit", "create", "upload", "delete", "move"]:
        if not self.r3_token:
            self.r3_token = self.make_new_r3_token()

        if not self.r3_token:
            printe.output(warn_err('<<red>> self.r3_token == "" '))

        params["token"] = self.r3_token

        params = self.filter_params(params)

        params.setdefault("formatversion", "1")

        data = self.make_response(params, files=files, do_error=do_error)

        if not data:
            printe.output("<<red>> super_login(post): not data. return {}.")
            return {}
        # ---
        error = data.get("error", {})
        # ---
        if error != {}:
            Invalid = error.get("info", "")
            error_code = error.get("code", "")
            # code = error.get("code", "")
            # ---
            if do_error:
                printe.output(f"<<red>> super_login(post): error: {error}")
            # ---
            if Invalid == "Invalid CSRF token.":
                printe.output(f'<<red>> ** error "Invalid CSRF token.".\n{self.r3_token} ')
                if CSRF:
                    # ---
                    self.r3_token = self.make_new_r3_token()
                    # ---
                    return self.post_params(params, Type=Type, addtoken=addtoken, CSRF=False)
            # ---
            error_code = error.get("code", "")
            # ---
            if error_code == "maxlag" and max_retry < 4:
                lage = int(error.get("lag", "0"))
                # ---
                test_print(params)
                # ---
                printe.output(f"<<purple>>post_params: <<red>> {lage=} {max_retry=}, sleep: {lage + 1}")
                # ---
                time.sleep(lage + 1)
                # ---
                ar_lag[1] = lage + 1
                # ---
                params["maxlag"] = ar_lag[1]
                # ---
                return self.post_params(params, Type=Type, addtoken=addtoken, max_retry=max_retry + 1)
            # ---
        if "printdata" in sys.argv:
            printe.output(data)

        return data

    def post_continue(self, params, action, _p_="pages", p_empty=None, Max=500000, first=False, _p_2="", _p_2_empty=None):
        # ---
        test_print("_______________________")
        test_print(f"post_continue, start. {action=}, {_p_=}")
        # ---
        if not isinstance(Max, int) and Max.isdigit():
            Max = int(Max)
        # ---
        if Max == 0:
            Max = 500000
        # ---
        p_empty = p_empty or []
        _p_2_empty = _p_2_empty or []
        # ---
        results = p_empty
        # ---
        continue_params = {}
        # ---
        d = 0
        # ---
        while continue_params != {} or d == 0:
            # ---
            params2 = copy.deepcopy(params)
            # ---
            d += 1
            # ---
            if continue_params:
                # params = {**params, **continue_params}
                test_print("continue_params:")
                for k, v in continue_params.items():
                    params2[k] = v
                # params2.update(continue_params)
                test_print(params2)
            # ---
            json1 = self.post_params(params2)
            # ---
            if not json1:
                test_print("post_continue, json1 is empty. break")
                break
            # ---
            continue_params = {}
            # ---
            if action == "wbsearchentities":
                data = json1.get("search", [])
                # ---
                # test_print("wbsearchentities json1: ")
                # test_print(str(json1))
                # ---
                # search_continue = json1.get("search-continue")
                # ---
                # if search_continue: continue_params = {"search-continue": search_continue}
            else:
                # ---
                continue_params = json1.get("continue", {})
                # ---
                data = json1.get(action, {}).get(_p_, p_empty)
                # ---
                if _p_ == "querypage":
                    data = data.get("results", [])
                elif first:
                    if isinstance(data, list) and len(data) > 0:
                        data = data[0]
                        if _p_2:
                            data = data.get(_p_2, _p_2_empty)
            # ---
            if not data:
                test_print("post continue, data is empty. break")
                break
            # ---
            test_print(f"post continue, len:{len(data)}, all: {len(results)}")
            # ---
            if Max <= len(results) and len(results) > 1:
                test_print(f"post continue, {Max=} <= {len(results)=}. break")
                break
            # ---
            if isinstance(results, list):
                results.extend(data)
                # results = list(set(results))
            else:
                print(f"{type(results)=}")
                print(f"{type(data)=}")
                results = {**results, **data}
        # ---
        test_print(f"post continue, {len(results)=}")
        # ---
        return results
