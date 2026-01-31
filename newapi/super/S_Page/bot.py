"""

from .super.S_Page.bot import PAGE_APIS

"""

from ..handel_errors import HANDEL_ERRORS


class PAGE_APIS(HANDEL_ERRORS):
    def __init__(self, login_bot):
        # print("class PAGE_APIS:")
        self.login_bot = login_bot
        # ---
        self.user_login = login_bot.user_login
        # ---
        self.title = getattr(self, "title", "")
        # ---
        super().__init__()

    def post_continue(
        self,
        params,
        action,
        _p_="pages",
        p_empty=None,
        Max=500000,
        first=False,
        _p_2="",
        _p_2_empty=None,
    ):
        return self.login_bot.post_continue(
            params,
            action,
            _p_=_p_,
            p_empty=p_empty,
            Max=Max,
            first=first,
            _p_2=_p_2,
            _p_2_empty=_p_2_empty,
        )
