"""

from .super.S_API.bot import BOTS_APIS

"""

import logging
import sys

from ...api_utils.ask_bot import ASK_BOT
from ..handel_errors import HANDEL_ERRORS

logger = logging.getLogger(__name__)

yes_answer = ["y", "a", "", "Y", "A", "all", "aaa"]
file_name = "bot_api.py"


class BOTS_APIS(HANDEL_ERRORS, ASK_BOT):
    def __init__(self):
        # print("class BOTS_APIS:")
        # ---
        self.username = getattr(self, "username", "")
        # ---
        super().__init__()

    def Add_To_Bottom(self, text, summary, title, poss="Head|Bottom"):
        # ---
        if not title.strip():
            logger.info('** .. title == ""')
            return False
        # ---
        if not text.strip():
            logger.info('** .. text == ""')
            return False
        # ---
        logger.debug(f"** .. [[{title}]] ")
        # printe.showDiff("", text)
        # ---
        user = self.username or getattr(self, "user_login", "")
        # ---
        ask = self.ask_put(
            newtext=text,
            message=f"** Add_To {poss} .. [[{title}]] ",
            job="Add_To_Bottom",
            username=user,
            summary=summary,
        )
        # ---
        if ask is False:
            return False
        # ---
        params = {
            "action": "edit",
            "format": "json",
            "title": title,
            "summary": summary,
            "notminor": 1,
            "nocreate": 1,
            "utf8": 1,
        }
        # ---
        if poss == "Head":
            params["prependtext"] = f"{text.strip()}\n"
        else:
            params["appendtext"] = f"\n{text.strip()}"
        # ---
        results = self.post_params(params)
        # ---
        if not results:
            return ""
        # ---
        data = results.get("edit", {})
        result = data.get("result", "")
        # ---
        if result == "Success":
            logger.info(f"<<lightgreen>>** True. title:({title})")
            return True
        # ---
        error = results.get("error", {})
        # ---
        if error != {}:
            print(results)
            er = self.handel_err(error, function="Add_To_Bottom", params=params)
            # ---
            return er
        # ---
        return True

    def move(
        self,
        old_title,
        to,
        reason="",
        noredirect=False,
        movesubpages=False,
        return_dict=False,
    ):
        # ---
        logger.info(f"<<lightyellow>> def [[{old_title}]] to [[{to}]] ")
        # ---
        params = {
            "action": "move",
            "format": "json",
            "from": old_title,
            "to": to,
            "movetalk": 1,
            "formatversion": 2,
        }
        # ---
        if noredirect:
            params["noredirect"] = 1
        if movesubpages:
            params["movesubpages"] = 1
        # ---
        if reason:
            params["reason"] = reason
        # ---
        if old_title == to:
            logger.debug(f"<<lightred>>** old_title == to {to} ")
            return {}
        # ---
        message = f"Do you want to move page:[[{old_title}]] to [[{to}]]?"
        # ---
        user = self.username or getattr(self, "user_login", "")
        # ---
        if not self.ask_put(message=message, job="move", username=user):
            return {}
        # ---
        data = self.post_params(params)
        # { "move": { "from": "d", "to": "d2", "reason": "wrong", "redirectcreated": true, "moveoverredirect": false } }
        # ---
        if not data:
            logger.info("no data")
            return {}
        # ---
        _expend_data = {
            "move": {
                "from": "User:Mr. Ibrahem",
                "to": "User:Mr. Ibrahem/x",
                "reason": "wrong title",
                "redirectcreated": True,
                "moveoverredirect": False,
                "talkmove-errors": [
                    {
                        "message": "content-not-allowed-here",
                        "params": [
                            "Structured Discussions board",
                            "User talk:Mr. Ibrahem/x",
                            "main",
                        ],
                        "code": "contentnotallowedhere",
                        "type": "error",
                    },
                    {
                        "message": "flow-error-allowcreation-flow-create-board",
                        "params": [],
                        "code": "flow-error-allowcreation-flow-create-board",
                        "type": "error",
                    },
                ],
                "subpages": {
                    "errors": [
                        {
                            "message": "cant-move-subpages",
                            "params": [],
                            "code": "cant-move-subpages",
                            "type": "error",
                        }
                    ]
                },
                "subpages-talk": {
                    "errors": [
                        {
                            "message": "cant-move-subpages",
                            "params": [],
                            "code": "cant-move-subpages",
                            "type": "error",
                        }
                    ]
                },
            }
        }
        # ---
        move_done = data.get("move", {})
        error = data.get("error", {})
        error_code = error.get("code", "")  # missingtitle
        # ---
        # elif "Please choose another name." in r4:
        # ---
        if move_done:
            logger.info("<<lightgreen>>** true.")
            # ---
            if return_dict:
                return move_done
            # ---
            return True
        # ---
        if error:
            if error_code == "ratelimited":
                logger.info("<<red>> ratelimited:")
                return self.move(
                    old_title,
                    to,
                    reason=reason,
                    noredirect=noredirect,
                    movesubpages=movesubpages,
                    return_dict=return_dict,
                )

            if error_code == "articleexists":
                logger.info("<<red>> articleexists")
                return "articleexists"

            logger.info("<<red>> error")
            logger.info(error)

            return {}
        # ---
        return {}

    def expandtemplates(self, text):
        # ---
        params = {
            "action": "expandtemplates",
            "format": "json",
            "text": text,
            "prop": "wikitext",
            "formatversion": 2,
        }
        # ---
        data = self.post_params(params)
        # ---
        if not data:
            return text
        # ---
        newtext = data.get("expandtemplates", {}).get("wikitext") or text
        # ---
        return newtext

    def Parse_Text(self, line, title):
        # ---
        params = {
            "action": "parse",
            "prop": "wikitext",
            "text": line,
            "title": title,
            "pst": 1,
            "contentmodel": "wikitext",
            "utf8": 1,
            "formatversion": 2,
        }
        # ---
        # {"parse": {"title": "كريس فروم", "pageid": 2639244, "wikitext": "{{subst:user:Mr._Ibrahem/line2|Q76|P31}}", "psttext": "\"Q76\":{\n\"P31\":\"إنسان\"\n\n\n\n\n},"}}
        # ---
        data = self.post_params(params)
        # ---
        if not data:
            return ""
        # ---
        textnew = data.get("parse", {}).get("psttext", "")
        # ---
        textnew = textnew.replace("\\n\\n", "")
        # ---
        return textnew

    def upload_by_file(
        self, file_name, text, file_path, comment="", ignorewarnings=False
    ):
        # ---
        logger.info(f"<<lightyellow>> def . {file_name=}")
        # ---
        if file_name.startswith("File:"):
            file_name = file_name.replace("File:", "")
        # ---
        if file_name.startswith("ملف:"):
            file_name = file_name.replace("ملف:", "")
        # ---
        logger.info(f"<<lightyellow>> {file_path=}...")
        # ---
        params = {
            "action": "upload",
            "format": "json",
            "filename": file_name,
            "comment": comment,
            "text": text,
            "utf8": 1,
        }
        # ---
        if ignorewarnings:
            params["ignorewarnings"] = 1
        # ---
        data = self.post_params(params, files={"file": open(file_path, "rb")})
        # ---
        upload_result = data.get("upload", {})
        # ---
        success = upload_result.get("result") == "Success"
        _error = data.get("error", {})
        # ---
        duplicate = (
            upload_result.get("warnings", {})
            .get("duplicate", [""])[0]
            .replace("_", " ")
        )
        # ---
        if success:
            logger.info(f"<<lightgreen>> ** upload true .. [[File:{file_name}]] ")
            return True
        # ---
        if duplicate:
            logger.info(f"<<lightred>> ** duplicate file: {duplicate}.")
        # ---
        return data

    def get_title_redirect_normalize(self, title, redirects, normalized):
        # ---
        redirects = redirects or []
        normalized = normalized or []
        # ---
        tab = {
            "user_input": title,
            "redirect_to": "",
            "normalized_to": "",
            "real_title": title,
        }
        # ---
        normalized = {x["to"]: x["from"] for x in normalized}
        # ---
        redirects = {x["to"]: x["from"] for x in redirects}
        # ---
        if tab["user_input"] in redirects:
            tab["redirect_to"] = tab["user_input"]
            tab["user_input"] = redirects[tab["user_input"]]
        # ---
        if tab["user_input"] in normalized:
            tab["normalized_to"] = tab["user_input"]
            tab["user_input"] = normalized[tab["user_input"]]
        # ---
        if tab["user_input"] == title:
            return {}
        # ---
        return tab

    def merge_all_jsons_deep(self, all_jsons, json1):
        def deep_merge(a, b):
            # إذا كان كلاهما dict → دمج مفاتيح
            if isinstance(a, dict) and isinstance(b, dict):
                for k, v in b.items():
                    if k in a:
                        a[k] = deep_merge(a[k], v)
                    else:
                        a[k] = v
                return a
            # إذا كان كلاهما list → تمديد القوائم
            elif isinstance(a, list) and isinstance(b, list):
                return a + b
            # في حالة اختلاف النوع → نأخذ الجديد
            else:
                return b

        # إذا لم يكن all_jsons dict نجعله dict
        if not isinstance(all_jsons, dict):
            all_jsons = {}

        return deep_merge(all_jsons, json1)

    def merge_all_jsons(self, all_jsons, json1):
        # --- إذا كان all_jsons ليس dict نحوله
        if not isinstance(all_jsons, dict):
            all_jsons = {}
        # ---
        # guard against non-dict inputs for json1
        if not isinstance(json1, dict):
            return all_jsons
        # ---
        for x, z in json1.items():
            if x not in all_jsons:
                all_jsons[x] = z
                continue
            # ---
            tab = all_jsons[x]
            # --- إذا كان كلاهما list
            if isinstance(tab, list) and isinstance(z, list):
                # explicit shallow copy of z to avoid surprises if z is reused
                tab.extend(list(z))
            # --- إذا كان كلاهما dict
            elif isinstance(tab, dict) and isinstance(z, dict):
                tab.update(z)
            # --- في حالة اختلاف النوع أو قيمة بسيطة
            else:
                all_jsons[x] = z
        # ---
        return all_jsons
