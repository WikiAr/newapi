"""

from .super.S_Page.bot import PageAPIS

"""

from ...client_wiki.api_utils.handel_errors import HandleErrors


class PageAPIS(HandleErrors):
    def __init__(self, login_bot):
        # print("class PageAPIS:")
        self.login_bot = login_bot
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
        max=500000,
        first=False,
        _p_2="",
        _p_2_empty=None,
    ):
        return self.login_bot.post_continue(
            params,
            action,
            _p_=_p_,
            p_empty=p_empty,
            max=max,
            first=first,
            _p_2=_p_2,
            _p_2_empty=_p_2_empty,
        )
