"""

from .super.S_Page.bot import PAGE_APIS

"""
from ..handel_errors import HANDEL_ERRORS

class PAGE_APIS(HANDEL_ERRORS):
    def __init__(self, login_bot):
        # print("class PAGE_APIS:")
        self.login_bot = login_bot
        # ---
        self.title = getattr(self, "title", "")
        self.lang = getattr(self, "lang", "")
        self.family = getattr(self, "family", "")
        self.endpoint = f"https://{self.lang}.{self.family}.org/w/api.php"
        # ---
        self.is_Disambig = getattr(self, "is_Disambig", False)
        self.can_be_edit = getattr(self, "can_be_edit", False)
        self.ns = getattr(self, "ns", False)
        # ---
        self.userinfo = getattr(self, "userinfo", {})
        self.create_data = getattr(self, "create_data", {})
        self.info = getattr(self, "info", {})
        # ---
        self.username = getattr(self, "username", "")
        self.Exists = getattr(self, "Exists", "")
        self.is_redirect = getattr(self, "is_redirect", "")
        self.flagged = getattr(self, "flagged", "")
        # ---
        self.wikibase_item = getattr(self, "wikibase_item", "")
        self.text = getattr(self, "text", "")
        self.text_html = getattr(self, "text_html", "")
        # ---
        self.touched = getattr(self, "touched", "")
        self.revid = getattr(self, "revid", "")
        self.newrevid = getattr(self, "newrevid", "")
        # ---
        self.pageid = getattr(self, "pageid", "")
        self.user = getattr(self, "user", "")
        # ---
        self.timestamp = getattr(self, "timestamp", "")
        self.summary = getattr(self, "summary", "")
        self.newtext = getattr(self, "newtext", "")
        # ---
        self.revisions = getattr(self, "revisions", [])
        self.back_links = getattr(self, "back_links", [])
        self.extlinks = getattr(self, "extlinks", [])
        self.links = getattr(self, "links", [])
        self.iwlinks = getattr(self, "iwlinks", [])
        self.links_here = getattr(self, "links_here", [])
        # ---
        self.categories = getattr(self, "categories", {})
        self.hidden_categories = getattr(self, "hidden_categories", {})
        self.all_categories_with_hidden = getattr(self, "all_categories_with_hidden", {})
        # ---
        self.langlinks = getattr(self, "langlinks", {})
        self.templates = getattr(self, "templates", {})
        self.templates_API = getattr(self, "templates_API", {})
        # ---
        self.words = getattr(self, "words", 0)
        self.length = getattr(self, "length", 0)
        # ---
        super().__init__()

    def post_continue(self, params, action, _p_="pages", p_empty=None, Max=500000, first=False, _p_2="", _p_2_empty=None):
        return self.login_bot.post_continue(
            params,
            action,
            _p_=_p_,
            p_empty=p_empty,
            Max=Max,
            first=first,
            _p_2=_p_2,
            _p_2_empty=_p_2_empty
        )

    def page_backlinks(self, ns=0):
        params = {
            "action": "query",
            "maxlag": "3",
            # "prop": "info",
            "generator": "backlinks",
            # "redirects": 1,
            # 'gblfilterredir': 'redirects',
            "gbltitle": self.title,
            "gblnamespace": ns,
            "gbllimit": "max",
            "formatversion": "2",
            "gblredirect": 1,
        }
        # ---
        # x = { 'batchcomplete': True, 'limits': { 'backlinks': 2500 }, 'query': { 'redirects': [{ 'from': 'فريدريش زيمرمان', 'to': 'فريدريش تسيمرمان' }], 'pages': [{ 'pageid': 2941285, 'ns': 0, 'title': 'فولفغانغ شويبله' }, { 'pageid': 4783977, 'ns': 0, 'title': 'وزارة الشؤون الرقمية والنقل' }, { 'pageid': 5218323, 'ns': 0, 'title': 'فريدريش تسيمرمان' }, { 'pageid': 6662649, 'ns': 0, 'title': 'غونتر كراوزه' }] } }
        # ---
        # data = self.post_params(params)
        # pages = data.get("query", {}).get("pages", [])
        # ---
        pages = self.post_continue(params, "query", _p_="pages", p_empty=[])
        # ---
        back_links = [x for x in pages if x["title"] != self.title]
        # ---
        self.back_links = back_links
        # ---
        return self.back_links

    def page_links(self):
        params = {
            "action": "parse",
            "prop": "links",
            "formatversion": "2",
            "page": self.title,
        }
        # data = self.post_params(params)
        # data = data.get('parse', {}).get('links', [])
        # ---
        data = self.post_continue(params, "parse", _p_="links", p_empty=[])
        # ---
        # [{'ns': 14, 'title': 'تصنيف:مقالات بحاجة لشريط بوابات', 'exists': True}, {'ns': 14, 'title': 'تصنيف:مقالات بحاجة لصندوق معلومات', 'exists': False}]
        # ---
        self.links = data
        # ---
        return self.links

    def page_links_query(self, plnamespace="*"):
        params = {
            "action": "query",
            "prop": "links",
            "formatversion": "2",
            "titles": self.title,
            "plnamespace": plnamespace,
            "pllimit": "max",
            "converttitles": 1,
        }
        # data = self.post_params(params)
        # data = data.get('query', {}).get('links', [])
        # ---
        data = self.post_continue(params, "query", _p_="links", p_empty=[])
        # ---
        # [{'ns': 14, 'title': 'تصنيف:مقالات بحاجة لشريط بوابات', 'exists': True}, {'ns': 14, 'title': 'تصنيف:مقالات بحاجة لصندوق معلومات', 'exists': False}]
        # ---
        self.links = data
        # ---
        return self.links

    def get_revisions(self, rvprops=[]):
        # ---
        rvprop = [
            "comment",
            "timestamp",
            "user",
            # "content",
            "ids",
        ]
        # ---
        for x in rvprops:
            if x not in rvprop:
                rvprop.append(x)
        # ---
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": self.title,
            "utf8": 1,
            "formatversion": "2",
            "rvdir": "newer",
            "rvslots": "*",
            "rvlimit": "max",
            # "rvprop": "comment|timestamp|user|content|ids",
            "rvprop": "|".join(rvprop),
        }
        # ---
        _revisions = self.post_continue(params, "query", _p_="pages", p_empty=[])
        # ---
        revisions = []
        # ---
        for x in _revisions:
            revisions.extend(x["revisions"])
        # ---
        self.revisions = revisions
        # ---
        return revisions
