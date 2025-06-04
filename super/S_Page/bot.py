"""

from .super.S_Page.bot import PAGE_APIS

"""
from ..handel_errors import HANDEL_ERRORS
# from ..S_Login.super_login import Login

class PAGE_APIS(HANDEL_ERRORS):
    def __init__(self, login_bot):
        super().__init__()
        # print("class PAGE_APIS:")
        self.login_bot = login_bot
        # ---
        self.title = getattr(self, "title") if hasattr(self, "title") else ""
        self.lang = getattr(self, "lang") if hasattr(self, "lang") else ""
        self.family = getattr(self, "family") if hasattr(self, "family") else ""
        self.endpoint = f"https://{self.lang}.{self.family}.org/w/api.php"
        # ---
        self.is_Disambig = getattr(self, "is_Disambig") if hasattr(self, "is_Disambig") else False
        self.can_be_edit = getattr(self, "can_be_edit") if hasattr(self, "can_be_edit") else False
        self.ns = getattr(self, "ns") if hasattr(self, "ns") else False
        # ---
        self.userinfo = getattr(self, "userinfo") if hasattr(self, "userinfo") else {}
        self.create_data = getattr(self, "create_data") if hasattr(self, "create_data") else {}
        self.info = getattr(self, "info") if hasattr(self, "info") else {}
        # ---
        self.username = getattr(self, "username") if hasattr(self, "username") else ""
        self.Exists = getattr(self, "Exists") if hasattr(self, "Exists") else ""
        self.is_redirect = getattr(self, "is_redirect") if hasattr(self, "is_redirect") else ""
        self.flagged = getattr(self, "flagged") if hasattr(self, "flagged") else ""
        # ---
        self.wikibase_item = getattr(self, "wikibase_item") if hasattr(self, "wikibase_item") else ""
        self.text = getattr(self, "text") if hasattr(self, "text") else ""
        self.text_html = getattr(self, "text_html") if hasattr(self, "text_html") else ""
        # ---
        self.touched = getattr(self, "touched") if hasattr(self, "touched") else ""
        self.revid = getattr(self, "revid") if hasattr(self, "revid") else ""
        self.newrevid = getattr(self, "newrevid") if hasattr(self, "newrevid") else ""
        # ---
        self.pageid = getattr(self, "pageid") if hasattr(self, "pageid") else ""
        self.user = getattr(self, "user") if hasattr(self, "user") else ""
        # ---
        self.timestamp = getattr(self, "timestamp") if hasattr(self, "timestamp") else ""
        self.summary = getattr(self, "summary") if hasattr(self, "summary") else ""
        self.newtext = getattr(self, "newtext") if hasattr(self, "newtext") else ""
        # ---
        self.revisions = getattr(self, "revisions") if hasattr(self, "revisions") else []
        self.back_links = getattr(self, "back_links") if hasattr(self, "back_links") else []
        self.extlinks = getattr(self, "extlinks") if hasattr(self, "extlinks") else []
        self.links = getattr(self, "links") if hasattr(self, "links") else []
        self.iwlinks = getattr(self, "iwlinks") if hasattr(self, "iwlinks") else []
        self.links_here = getattr(self, "links_here") if hasattr(self, "links_here") else []
        # ---
        self.categories = getattr(self, "categories") if hasattr(self, "categories") else {}
        self.hidden_categories = getattr(self, "hidden_categories") if hasattr(self, "hidden_categories") else {}
        self.all_categories_with_hidden = getattr(self, "all_categories_with_hidden") if hasattr(self, "all_categories_with_hidden") else {}
        # ---
        self.langlinks = getattr(self, "langlinks") if hasattr(self, "langlinks") else {}
        self.templates = getattr(self, "templates") if hasattr(self, "templates") else {}
        self.templates_API = getattr(self, "templates_API") if hasattr(self, "templates_API") else {}
        # ---
        self.words = getattr(self, "words") if hasattr(self, "words") else 0
        self.length = getattr(self, "length") if hasattr(self, "length") else 0

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
