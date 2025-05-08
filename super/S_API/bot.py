"""

from newapi.super.S_API.bot import BOTS_APIS

"""
import sys
from newapi import printe
from newapi.super.handel_errors import HANDEL_ERRORS

yes_answer = ["y", "a", "", "Y", "A", "all", "aaa"]
Save_Edit_Pages = {1: False}
file_name = "bot_api.py"


def test_print(s):
    if "test_print" in sys.argv:
        printe.output(s)


class BOTS_APIS(HANDEL_ERRORS):
    def __init__(self):
        # print("class APIS:")
        self.username = ""
        super().__init__()

    def ask_put(self, nodiff=False, newtext="", text=""):
        yes_answer = ["y", "a", "", "Y", "A", "all", "aaa"]
        # ---
        if "ask" in sys.argv and not Save_Edit_Pages[1]:
            # ---
            if "nodiff" not in sys.argv and not nodiff:
                if len(newtext) < 70000 and len(text) < 70000 or "diff" in sys.argv:
                    printe.showDiff(text, newtext)
                else:
                    printe.output("showDiff error..")
                    printe.output(f"diference in bytes: {len(newtext) - len(text)}")
                    printe.output(f"length of text: {len(text)}, length of newtext: {len(newtext)}")
            # ---
            printe.output(f"<<lightyellow>>bot_api.py: save (yes, no)? {self.username=}")
            sa = input("([y]es, [N]o, [a]ll)?")
            # ---
            if sa == "a":
                printe.output("<<lightgreen>> ---------------------------------")
                printe.output(f"<<lightgreen>> {file_name} save all without asking.")
                printe.output("<<lightgreen>> ---------------------------------")
                Save_Edit_Pages[1] = True
            # ---
            if sa not in yes_answer:
                printe.output("wrong answer")
                return False
        # ---
        return True

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
        test_print(f"** Add_To_Bottom .. [[{title}]] ")
        # printe.showDiff("", text)
        # ---
        ask = self.ask_put(newtext=text, text="")
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
            test_print(f"<<lightred>>** old_title == to {to} ")
            return {}
        # ---
        if not self.save_move and "ask" in sys.argv:
            printe.output(f"<<lightyellow>>bot_api: Do you move page:[[{old_title}]] to [[{to}]]? {self.username=}")
            sa = input("([y]es, [N]o, [a]ll)?")
            # ---
            if sa == "a":
                printe.output("<<lightgreen>> ---------------------------------")
                printe.output("<<lightgreen>> bot_api.py move all without asking.")
                printe.output("<<lightgreen>> ---------------------------------")
                self.save_move = True
            # ---
            if sa not in yes_answer:
                printe.output("<<red>> bot_api: wrong answer")
                return {}
            # ---
            test_print(f"<<lightgreen>> answer: {sa in yes_answer}")
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
        error = data.get("error", {})
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
