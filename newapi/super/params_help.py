"""

from .super.params_help import PARAMS_HELPS

"""
import sys
import json
from ..api_utils.except_err import exception_err
from ..config import settings


class PARAMS_HELPS:
    def __init__(self) -> None:
        self.lang = getattr(self, "lang", "")
        self.family = getattr(self, "family", "")
        self.username = getattr(self, "username", "")
        self.Bot_or_himo = getattr(self, "Bot_or_himo", "")
        self.url_o_print = getattr(self, "url_o_print", "")
        # pass

    def params_w(self, params) -> dict:
        if self.family == "wikipedia" and self.lang == "ar" and params.get("summary") and self.username.find("bot") == -1 and not settings.flags.ibrahemsummary:
            params["summary"] = ""

        self.Bot_or_himo = 1 if "bot" in self.username else 0

        if self.family != "nccommons":
            params["bot"] = self.Bot_or_himo

        if "minor" in params and params["minor"] == "":
            params["minor"] = self.Bot_or_himo

        if self.family != "toolforge":
            if params["action"] in ["edit", "create", "upload", "delete", "move"] or params["action"].startswith("wb") or self.family == "wikidata":
                if not settings.flags.nologin and self.username:
                    params["assertuser"] = self.username

        return params

    def parse_data(self, req0) -> dict:
        """
        Parse JSON response data.
        """
        text = ""
        try:
            data = req0 if isinstance(req0, dict) else req0.json()

            if data.get("error", {}).get("*", "").find("mailing list") > -1:
                data["error"]["*"] = ""
            if data.get("servedby"):
                data["servedby"] = ""

            return data
        except Exception as e:
            exception_err(e)
            text = str(req0.text).strip()

        valid_text = text.startswith("{") and text.endswith("}")

        if not text or not valid_text:
            return {}

        try:
            data = json.loads(text)
            return data
        except Exception as e:
            exception_err(e, self.url_o_print)

        return {}
