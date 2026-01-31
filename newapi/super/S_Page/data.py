"""

from .data import Content, Meta, RevisionsData, LinksData, CategoriesData, TemplateData

(Exists|all_categories_with_hidden|back_links|can_be_edit|categories|create_data|extlinks|flagged|hidden_categories|info|is_Disambig|is_redirect|iwlinks|length|links_here|links|newrevid|pageid|revid|revisions|summary|templates|templates_API|text_html|timestamp|touched|userinfo|username|wikibase_item|words)

"""

from dataclasses import dataclass, field

r"""
# content
self.text = ""
self.newtext = ""
self.text_html = ""
self.summary = ""
self.words = 0
self.length = 0
# ---
self\.(text_html|words|length|summary)
self.content.$1
"""


@dataclass
class Content:
    # text: str = ""
    # newtext: str = ""
    text_html: str = ""
    summary: str = ""
    words: int = 0
    length: int = 0


r"""
# meta
self.is_Disambig = False
self.can_be_edit = False
self.userinfo = {}
self.create_data = {}
self.info = {"done": False}
self.username = getattr(self, "username", "")
self.Exists = ""
self.is_redirect = ""
self.flagged = ""
self.wikibase_item = ""
# ---
self\.(is_Disambig|can_be_edit|userinfo|create_data|info|username|Exists|is_redirect|flagged|wikibase_item)
self.meta.$1
"""


@dataclass
class Meta:
    is_Disambig: bool = False
    can_be_edit: bool = False
    # ns: int = 0
    userinfo: dict = field(default_factory=dict)
    create_data: dict = field(default_factory=dict)
    info: dict = field(default_factory=lambda: {"done": False})
    username: str = ""
    Exists: str = ""
    is_redirect: str = ""
    flagged: str = ""
    wikibase_item: str = ""


r"""
# revisions_data
self.revid = ""
self.newrevid = ""
self.pageid = ""
self.timestamp = ""
self.revisions = []
self.touched = ""
# ---
self\.(revid|newrevid|pageid|timestamp|revisions|touched)
self.revisions_data.$1
"""


@dataclass
class RevisionsData:
    revid: str = ""
    newrevid: str = ""
    pageid: str = ""
    timestamp: str = ""
    revisions: list = field(default_factory=list)
    touched: str = ""


r"""
# LinksData
self.back_links = []
self.extlinks = []
self.links = []
self.links2 = []
self.iwlinks = []
self.links_here = []
# ---
self\.(back_links|links_here|extlinks|links|iwlinks)
self.links_data.$1
"""


@dataclass
class LinksData:
    back_links: list = field(default_factory=list)
    extlinks: list = field(default_factory=list)
    iwlinks: list = field(default_factory=list)
    links_here: list = field(default_factory=list)
    links: list = field(default_factory=list)
    links2: list = field(default_factory=list)


r"""
# CategoriesData
self.categories = {}
self.hidden_categories = {}
self.all_categories_with_hidden = {}
# ---
self\.(categories|hidden_categories|all_categories_with_hidden)
self.categories_data.$1
"""


@dataclass
class CategoriesData:
    categories: dict = field(default_factory=dict)
    hidden_categories: dict = field(default_factory=dict)
    all_categories_with_hidden: dict = field(default_factory=dict)


r"""
# TemplateData
self.templates = {}
self.templates_API = {}
# ---
self\.(templates_API|templates)
self.template_data.$1
"""


@dataclass
class TemplateData:
    templates: dict = field(default_factory=dict)
    templates_API: dict = field(default_factory=dict)
