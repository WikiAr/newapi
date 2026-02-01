"""

from ...api_utils.ask_bot import ASK_BOT

"""

import sys

from . import printe

yes_answer = ["y", "a", "", "Y", "A", "all", "aaa"]

Save_or_Ask = {}


class ASK_BOT:
    def __init__(self):
        pass

    def ask_put(self, nodiff=False, newtext="", text="", message="", job="Genral", username="", summary=""):
        """
        Prompts the user to confirm saving changes to a page, optionally displaying a diff.

        If enabled by command-line arguments or parameters, shows the difference between the current and new text, displays summary information, and asks the user to accept or reject the changes. Supports skipping further prompts for subsequent edits.

        Args:
            nodiff: If True, skips displaying the diff.

        Returns:
            True if the user accepts the changes or prompting is not required; False otherwise.
        """
        message = message or "Do you want to accept these changes?"
        # ---
        if "ask" in sys.argv and not Save_or_Ask.get(job):
            # ---
            if text or newtext:
                if "nodiff" not in sys.argv and not nodiff:
                    if len(newtext) < 70000 and len(text) < 70000 or "diff" in sys.argv:
                        printe.showDiff(text, newtext)
                    else:
                        printe.output("showDiff error..")
                # ---
                printe.output(f"diference in bytes: {len(newtext) - len(text):,}")
                printe.output(f"len of text: {len(text):,}, len of newtext: {len(newtext):,}")
            # ---
            if summary:
                printe.output(f"-Edit summary: {summary}")
            # ---
            printe.output(f"<<lightyellow>>ASK_BOT: {message}? (yes, no) {username=}")
            # ---
            sa = input("([y]es, [N]o, [a]ll)?")
            # ---
            if sa == "a":
                Save_or_Ask[job] = True
                # ---
                printe.output("<<lightgreen>> ---------------------------------")
                printe.output(f"<<lightgreen>> save all:{job} without asking.")
                printe.output("<<lightgreen>> ---------------------------------")
            # ---
            if sa not in yes_answer:
                printe.output("wrong answer")
                return False
        # ---
        return True
