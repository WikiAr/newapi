"""

from .data import Content, Meta, RevisionsData, LinksData, CategoriesData, TemplateData

(Exists|all_categories_with_hidden|back_links|can_be_edit|categories|create_data|extlinks|flagged|hidden_categories|info|is_disambig|is_redirect|iwlinks|length|links_here|links|newrevid|pageid|revid|revisions|summary|templates|templates_api|text_html|timestamp|touched|userinfo|username|wikibase_item|words)

"""

from dataclasses import dataclass, field


@dataclass
class Content:
    # text: str = ""
    # newtext: str = ""
    text_html: str = ""
    summary: str = ""
    words: int = 0
    length: int = 0


@dataclass
class Meta:
    is_disambig: bool = False
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


@dataclass
class RevisionsData:
    revid: str = ""
    newrevid: str = ""
    pageid: str = ""
    timestamp: str = ""
    revisions: list = field(default_factory=list)
    touched: str = ""


@dataclass
class LinksData:
    back_links: list = field(default_factory=list)
    extlinks: list = field(default_factory=list)
    iwlinks: list = field(default_factory=list)
    links_here: list = field(default_factory=list)
    links: list = field(default_factory=list)
    links2: list = field(default_factory=list)


@dataclass
class CategoriesData:
    categories: dict = field(default_factory=dict)
    hidden_categories: dict = field(default_factory=dict)
    all_categories_with_hidden: dict = field(default_factory=dict)


@dataclass
class TemplateData:
    templates: dict = field(default_factory=dict)
    templates_api: dict = field(default_factory=dict)
