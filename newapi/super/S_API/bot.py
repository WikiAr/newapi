"""

from .super.S_API.bot import BOTS_APIS

"""
import sys
from ...api_utils import printe
from ..handel_errors import HANDEL_ERRORS
from ...api_utils.ask_bot import ASK_BOT

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
            printe.output('** Add_To_Bottom ..  title == ""')
            return False
        # ---
        if not text.strip():
            printe.output('** Add_To_Bottom ..  text == ""')
            return False
        # ---
        printe.test_print(f"** Add_To_Bottom .. [[{title}]] ")
        # printe.showDiff("", text)
        # ---
        user = self.username or getattr(self, 'user_login', '')
        # ---
        ask = self.ask_put(newtext=text, message=f"** Add_To {poss} .. [[{title}]] ", job="Add_To_Bottom", username=user, summary=summary)
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
            printe.output(f"<<lightgreen>>** True. Add_To_Bottom title:({title})")
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

    def move(self, old_title, to, reason="", noredirect=False, movesubpages=False, return_dict=False):
        # ---
        printe.output(f"<<lightyellow>> def move [[{old_title}]] to [[{to}]] ")
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
            printe.test_print(f"<<lightred>>** old_title == to {to} ")
            return {}
        # ---
        message = f"Do you want to move page:[[{old_title}]] to [[{to}]]?"
        # ---
        user = self.username or getattr(self, 'user_login', '')
        # ---
        if not self.ask_put(message=message, job="move", username=user):
            return {}
        # ---
        data = self.post_params(params)
        # { "move": { "from": "d", "to": "d2", "reason": "wrong", "redirectcreated": true, "moveoverredirect": false } }
        # ---
        if not data:
            printe.output("no data")
            return {}
        # ---
        _expend_data = {
            "move": {
                "from": "User:Mr. Ibrahem",
                "to": "User:Mr. Ibrahem/x",
                "reason": "wrong title",
                "redirectcreated": True,
                "moveoverredirect": False,
                "talkmove-errors": [{"message": "content-not-allowed-here", "params": ["Structured Discussions board", "User talk:Mr. Ibrahem/x", "main"], "code": "contentnotallowedhere", "type": "error"}, {"message": "flow-error-allowcreation-flow-create-board", "params": [], "code": "flow-error-allowcreation-flow-create-board", "type": "error"}],
                "subpages": {"errors": [{"message": "cant-move-subpages", "params": [], "code": "cant-move-subpages", "type": "error"}]},
                "subpages-talk": {"errors": [{"message": "cant-move-subpages", "params": [], "code": "cant-move-subpages", "type": "error"}]},
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
            printe.output("<<lightgreen>>** true.")
            # ---
            if return_dict:
                return move_done
            # ---
            return True
        # ---
        if error:
            if error_code == "ratelimited":
                printe.output("<<red>> move ratelimited:")
                return self.move(old_title, to, reason=reason, noredirect=noredirect, movesubpages=movesubpages, return_dict=return_dict)

            if error_code == "articleexists":
                printe.output("<<red>> articleexists")
                return "articleexists"

            printe.output("<<red>> error")
            printe.output(error)

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

    def upload_by_file(self, file_name, text, file_path, comment="", ignorewarnings=False):
        # ---
        printe.output(f"<<lightyellow>> def upload_by_file. {file_name=}")
        # ---
        if file_name.startswith("File:"):
            file_name = file_name.replace("File:", "")
        # ---
        if file_name.startswith("ملف:"):
            file_name = file_name.replace("ملف:", "")
        # ---
        printe.output(f"<<lightyellow>> {file_path=}...")
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
        duplicate = upload_result.get("warnings", {}).get("duplicate", [""])[0].replace("_", " ")
        # ---
        if success:
            printe.output(f"<<lightgreen>> ** upload true .. [[File:{file_name}]] ")
            return True
        # ---
        if duplicate:
            printe.output(f"<<lightred>> ** duplicate file: {duplicate}.")
        # ---
        return data
