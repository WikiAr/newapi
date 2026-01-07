"""
Usage:
# ---
from newapi.mdwiki_page import MainPage
page      = MainPage(title, 'www', family='mdwiki')
# ---
from newapi.page import MainPage
page      = MainPage(title, 'ar', family='wikipedia')
# ---
'''
if not page.exists(): return
# ---
page_edit = page.can_edit(script='fixref|cat|stub|tempcat|portal')
if not page_edit: return
# ---
if page.isDisambiguation() :  return
# ---
if page.isRedirect() :  return
# target = page.get_redirect_target()
# ---
text        = page.get_text()
ns          = page.namespace()
links       = page.page_links()
categories  = page.get_categories(with_hidden=False)
langlinks   = page.get_langlinks()
wiki_links  = page.get_wiki_links_from_text()
refs        = page.Get_tags(tag='ref')# for x in ref: name, contents = x.name, x.contents
words       = page.get_words()
templates   = page.get_templates()
temps_API   = page.get_templates_API()
save_page   = page.save(newtext='', summary='', nocreate=1, minor='')
create      = page.Create(text='', summary='')
# ---
create_data = page.get_create_data() # { "timestamp" : "", "user" : "", "anon" : "" }
# ---
extlinks    = page.get_extlinks()
back_links  = page.page_backlinks()
text_html   = page.get_text_html()
hidden_categories= page.get_hidden_categories()
flagged     = page.is_flagged()
timestamp   = page.get_timestamp()
user        = page.get_user()
userinfo    = page.get_userinfo() # "id", "name", "groups"
revisions   = page.get_revisions(rvprops=['content'])
purge       = page.purge()
'''

"""
import os
from warnings import warn
import sys
import wikitextparser as wtp

from .ar_err import find_edit_error
from .bot import PAGE_APIS
from .data import Content, Meta, RevisionsData, LinksData, CategoriesData, TemplateData

from ...api_utils import printe, txtlib, botEdit
from ...api_utils.except_err import exception_err, warn_err
from ...api_utils.ask_bot import ASK_BOT
from ...api_utils.lang_codes import change_codes

print_test = {1: "test" in sys.argv}


class MainPage(PAGE_APIS, ASK_BOT):
    def __init__(self, login_bot, title, lang="", family="wikipedia"):
        # print(f"class MainPage: {lang=}")
        # ---
        """
        Initializes a MainPage instance for interacting with a MediaWiki page.

        Sets up page attributes including title, language, family, API endpoint, and metadata fields. Normalizes the language code, loads user tables if available, and logs into the wiki if required.
        """
        # ---
        self.login_bot = login_bot
        # ---
        self.user_login = login_bot.user_login
        # ---
        self.title = title
        self.lang = change_codes.get(lang) or lang
        self.family = family
        self.endpoint = f"https://{self.lang}.{self.family}.org/w/api.php"
        # ---
        self.text = ""
        self.newtext = ""
        self.ns = False
        self.langlinks = {}
        # ---
        self.meta = Meta()
        self.content = Content()
        self.revisions_data = RevisionsData()
        self.links_data = LinksData()
        self.categories_data = CategoriesData()
        self.template_data = TemplateData()
        # ---
        self.user = ""
        # ---
        super().__init__(login_bot)

    def post_params(self, params, Type="get", addtoken=False, GET_CSRF=True, files=None, do_error=False, max_retry=0):
        # ---
        return self.login_bot.post_params(
            params,
            Type=Type,
            addtoken=addtoken,
            GET_CSRF=GET_CSRF,
            files=files,
            do_error=do_error,
            max_retry=max_retry
        )

    def false_edit(self):
        # self.newtext
        # self.text
        # ---
        """
        Determines if a proposed edit should be considered erroneous and aborted.

        Returns True if the edit is likely to be a false or destructive edit, such as removing over 90% of the page content or matching language-specific error conditions (e.g., for Arabic pages). Returns False if the edit is allowed or if the page is not in the main namespace.
        """
        if self.ns is False or self.ns != 0:
            return False
        # ---
        if "nofa" in sys.argv:
            return False
        # ---
        if not self.text:
            self.text = self.get_text()
        # ---
        # If the new edit will remove 90% of the text, return False
        if len(self.newtext) < 0.1 * len(self.text):
            text_err = f"Edit will remove 90% of the text. {len(self.newtext)} < 0.1 * {len(self.text)}"
            text_err += f"title: {self.title}, summary: {self.content.summary}"
            exception_err("", text=text_err)
            return True
        # ---
        if self.lang == "ar" and self.ns == 0:
            if find_edit_error(self.text, self.newtext):
                return True
        # ---
        return False

    def import_page(self, family="wikipedia"):
        """
        Imports the page from another wiki family using the MediaWiki API.

        Args:
            family: The source wiki family from which to import the page (default is "wikipedia").

        Returns:
            The API response data from the import operation.
        """
        params = {
            "action": "import",
            "format": "json",
            "interwikisource": family,
            "interwikipage": self.title,
            "fullhistory": 1,
            "assignknownusers": 1,
        }
        # ---
        data = self.post_params(params)
        # ---
        done = data.get("import", [{}])[0].get("revisions", 0)
        # ---
        printe.output(f"<<lightgreen>> imported {done} revisions")
        # ---
        return data

    def find_create_data(self):
        """
        Retrieves and stores the creation metadata of the page's first revision.

        Queries the MediaWiki API for the earliest revision of the page and extracts the creation timestamp, user, and anonymity status. The data is stored in the `create_data` attribute and returned as a dictionary.

        Returns:
            dict: A dictionary containing 'timestamp', 'user', and 'anon' keys for the page's creation.
        """
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": self.title,
            "rvprop": "timestamp|ids|user",
            "rvslots": "*",
            "rvlimit": "1",
            "rvdir": "newer"
        }
        # ---
        data = self.post_params(params)
        # ---
        pages = data.get("query", {}).get("pages", {})
        # ---
        for _, v in pages.items():
            # ---
            page_data = v.get("revisions", [{}])[0]
            # ---
            if "parentid" in page_data and page_data["parentid"] == 0:
                self.meta.create_data = {
                    "timestamp" : page_data["timestamp"],
                    "user" : page_data.get("user", ""),
                    "anon" : page_data.get("anon", False),
                }
            # ---
            break
        # ---
        return self.meta.create_data

    def get_text(self, redirects=False):
        """
        Retrieves the current wikitext content and metadata for the page.

        Fetches the latest revision's wikitext, user, revision ID, timestamp, namespace, Wikibase item, and flagged status. Updates instance attributes with the retrieved data. If the revision is the first (creation), stores creation metadata. Returns the page's wikitext content.

        Args:
            redirects: If True, follows redirects to the target page.

        Returns:
            The wikitext content of the page.
        """
        params = {
            "action": "query",
            "prop": "revisions|pageprops|flagged",
            "titles": self.title,
            "ppprop": "wikibase_item",
            "rvprop": "timestamp|content|user|ids",
            "rvslots": "*",
        }  # pageprops  # revisions  # revisions
        # ---
        if redirects:
            params["redirects"] = 1
        data = self.post_params(params)
        # ---
        # _dat_ = { "batchcomplete": "", "query": { "normalized": [{ "from": "وب:ملعب", "to": "ويكيبيديا:ملعب" }], "pages": { "361534": { "pageid": 361534, "ns": 4, "title": "ويكيبيديا:ملعب", "revisions": [{ "revid": 61421668, "parentid": 61421528, "user": "Al-shazali Sabeel", "timestamp": "2023-03-07T13:50:29Z", "slots": { "main": { "contentmodel": "wikitext", "contentformat": "text/x-wiki", "*": "{{عنوان الملعب}}" } } }], "pageprops": { "wikibase_item": "Q3938" } } } }, }
        # ---
        pages = data.get("query", {}).get("pages", {})
        # ---
        for k, v in pages.items():
            # ---
            if print_test[1] or "printdata" in sys.argv:
                warn(warn_err(f"v:{str(v)}"), UserWarning)
            # ---
            if "ns" in v:
                self.ns = v["ns"]  # ns = 0 !
            # ---
            if "missing" in v or k == "-1":
                self.meta.Exists = False
                # break
            else:
                self.meta.Exists = True
            # ---
            # title = v["title"]
            # ---
            pageprops = v.get("pageprops", {})
            self.meta.wikibase_item = pageprops.get("wikibase_item") or self.meta.wikibase_item
            # ---
            # "flagged": { "stable_revid": 61366100, "level": 0, "level_text": "stable"}
            self.meta.flagged = v.get("flagged", False) is not False
            # ---
            self.revisions_data.pageid = v.get("pageid") or self.revisions_data.pageid
            # ---
            page_data = v.get("revisions", [{}])[0]
            # ---
            self.text = page_data.get("slots", {}).get("main", {}).get("*", "")
            self.user = page_data.get("user") or self.user
            self.revisions_data.revid = page_data.get("revid") or self.revisions_data.revid
            # ---
            self.revisions_data.timestamp = page_data.get("timestamp") or self.revisions_data.timestamp
            # ---
            if "parentid" in page_data and page_data["parentid"] == 0:
                self.meta.create_data = {
                    "timestamp" : page_data["timestamp"],
                    "user" : page_data.get("user", ""),
                    "anon" : page_data.get("anon", False),
                }
            # ---
            break
        # ---
        return self.text

    def get_qid(self):
        """Retrieve the QID from the wikibase item.

        This function checks if the `wikibase_item` attribute is set. If it is
        not set, it calls the `get_text` method to populate the `wikibase_item`.
        Finally, it returns the current value of `wikibase_item`.

        Returns:
            str: The QID associated with the wikibase item.
        """

        if not self.meta.wikibase_item:
            self.get_text()
        return self.meta.wikibase_item

    def get_infos(self):
        # ---
        """
        Fetches and updates comprehensive metadata for the current page from the MediaWiki API.

        Retrieves and stores categories (including hidden), language links, templates, backlinks, interwiki links, and page information such as namespace, page ID, length, last revision ID, and last touched timestamp. Updates instance attributes with the fetched data for later access.
        """
        params = {
            "action": "query",
            "titles": self.title,
            "prop": "categories|langlinks|templates|linkshere|iwlinks|info",
            "clprop": "sortkey|hidden",
            "cllimit": "max",  # categories
            "lllimit": "max",  # langlinks
            "tllimit": "max",  # templates
            "lhlimit": "max",  # linkshere
            "iwlimit": "max",  # iwlinks
            "formatversion": "2",
            # "normalize": 1,
            "tlnamespace": "10",
        }
        # ---
        # _data_ = { "continue": {}, "query": { "pages": { "9124097": { "pageid": 9124097, "ns": 0, "title": "طواف العالم للدراجات 2023", "categories": [], "langlinks": [], "templates": [{ "ns": 10, "title": "قالب:-" }], "linkshere": [{ "pageid": 189150, "ns": 0, "title": "طواف فرنسا" }], "iwlinks": [{ "prefix": "commons", "*": "Category:2023_UCI_World_Tour" }], "contentmodel": "wikitext", "pagelanguage": "ar", "pagelanguagehtmlcode": "ar", "pagelanguagedir": "rtl", "touched": "2023-03-07T11:53:53Z", "lastrevid": 61366100, "length": 985, } } }, }
        # ---
        data = self.post_params(params)
        # ---
        # xs = { 'batchcomplete': True, 'query': { 'pages': [{ 'pageid': 151314, 'ns': 10, 'title': 'قالب:أوب', 'categories': [{ 'ns': 14, 'title': 'تصنيف:قوالب تستخدم أنماط القوالب', 'sortkey': '', 'sortkeyprefix': '', 'hidden': False }, { 'ns': 14, 'title': 'تصنيف:cc', 'sortkey': 'v', 'sortkeyprefix': 'أوب', 'hidden': True }], 'langlinks': [{ 'lang': 'bh', 'title': 'टेम्पलेट:AWB' }], 'templates': [{ 'ns': 10, 'title': 'قالب:No redirect' }], 'linkshere': [{ 'pageid': 308641, 'ns': 10, 'title': 'قالب:AWB', 'redirect': True }], 'iwlinks': [{ 'prefix': 'd', 'title': 'Q4063270' }], 'contentmodel': 'wikitext', 'pagelanguage': 'ar', 'pagelanguagehtmlcode': 'ar', 'pagelanguagedir': 'rtl', 'touched': '2023-03-05T22:10:23Z', 'lastrevid': 61388266, 'length': 3477, }] }, }
        # ---
        ta = data.get("query", {}).get("pages", [{}])[0]
        # ---
        # for _, ta in pages.items():
        # ---
        # self.ns = ta.get("ns") or self.ns
        if "ns" in ta:
            self.ns = ta["ns"]  # ns = 0 !
        # ---
        self.revisions_data.pageid = ta.get("pageid") or self.revisions_data.pageid
        self.content.length = ta.get("length") or self.content.length
        self.revisions_data.revid = ta.get("lastrevid") or self.revisions_data.revid
        self.revisions_data.touched = ta.get("touched") or self.revisions_data.touched
        # ---
        self.meta.is_redirect = True if "redirect" in ta else False
        # ---
        for cat in ta.get("categories", []):
            # ---
            # _cat_ = { "ns": 14, "title": "تصنيف:بوابة سباق الدراجات الهوائية/مقالات متعلقة", "sortkey": "d8b7", "sortkeyprefix": "", "hidden": True }
            # ---
            if "sortkey" in cat:
                del cat["sortkey"]
            # ---
            tit = cat["title"]
            # ---
            self.categories_data.all_categories_with_hidden[tit] = cat
            # ---
            if cat.get("hidden") is True:
                self.categories_data.hidden_categories[tit] = cat
            else:
                del cat["hidden"]
                self.categories_data.categories[tit] = cat
        # ---
        if ta.get("langlinks", []) != []:
            # ---
            # {"lang": "ca", "*": "UCI World Tour 2023"} or {'lang': 'bh', 'title': 'टेम्पलेट:AWB'}
            # ---
            self.langlinks = {ta["lang"]: ta.get("*") or ta.get("title") for ta in ta.get("langlinks", [])}
        # ---
        if ta.get("templates", []) != []:
            # ---
            # 'templates': [{'ns': 10, 'title': 'قالب:No redirect'}],
            # ---
            self.template_data.templates_API = [ta["title"] for ta in ta.get("templates", [])]
        # ---
        # "linkshere": [{"pageid": 189150,"ns": 0,"title": "طواف فرنسا"}, {"pageid": 308641,"ns": 10,"title": "قالب:AWB","redirect": ""}]
        self.links_data.links_here = ta.get("linkshere", [])
        # ---
        self.links_data.iwlinks = ta.get("iwlinks", [])
        # ---
        self.meta.info["done"] = True

    def get_text_html(self):
        params = {
            "action": "parse",
            "page": self.title,
            "formatversion": "2",
            "prop": "text",
        }
        # ---
        data = self.post_params(params)
        # ---
        # _data_ = { 'warnings': { 'main': { 'warnings': 'Unrecognized parameter: bot.' } }, 'parse': { 'title': 'ويكيبيديا:ملعب', 'pageid': 361534, 'text': '' } }
        # ---
        self.content.text_html = data.get("parse", {}).get("text", "")
        # ---
        return self.content.text_html

    def get_redirect_target(self):
        # ---
        params = {
            "action": "query",
            "titles": self.title,
            "prop": "info",
            "redirects": 1,
        }
        # ---
        data = self.post_params(params)
        # ---
        # _pages_ = { 'batchcomplete': '', 'query': { 'redirects': [{ 'from': 'Yemen', 'to': 'اليمن' }], 'pages': {}, 'normalized': [{ 'from': 'yemen', 'to': 'Yemen' }] } }
        # ---
        _redirects = {"from": "Yemen", "to": "اليمن"}
        # ---
        redirects = data.get("query", {}).get("redirects", [{}])[0]
        # ---
        to = redirects.get("to", "")
        # ---
        if to:
            printe.output(f"<<lightyellow>>Page:({self.title}) redirect to ({to})")
        # ---
        return to

    def get_words(self):
        srlimit = "30"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": self.title,
            "srlimit": srlimit,
        }
        data = self.post_params(params, addtoken=True)
        # ---
        if not data:
            return 0
        # ---
        search = data.get("query", {}).get("search", [])
        # ---
        for pag in search:
            tit = pag["title"]
            if tit == self.title:
                count = pag["wordcount"]
                self.content.words = count
                break
        # ---
        return self.content.words

    def get_extlinks(self):
        params = {
            "action": "query",
            "format": "json",
            "prop": "extlinks",
            "titles": self.title,
            "formatversion": "2",
            "utf8": 1,
            "ellimit": "max",
        }
        # ---
        links = []
        # ---
        continue_params = {}
        # ---
        d = 0
        # ---
        while continue_params != {} or d == 0:
            # ---
            d += 1
            # ---
            if continue_params:
                # params = {**params, **continue_params}
                params.update(continue_params)
            # ---
            json1 = self.post_params(params)
            # ---
            continue_params = json1.get("continue", {})
            # ---
            linkso = json1.get("query", {}).get("pages", [{}])[0].get("extlinks", [])
            # ---
            links.extend(linkso)
        # ---
        links = [x["url"] for x in links]
        # ---
        # remove duplicates
        liste1 = sorted(set(links))
        # ---
        self.links_data.extlinks = liste1
        return liste1

    def get_userinfo(self):
        if len(self.meta.userinfo) == 0:
            params = {
                "action": "query",
                "format": "json",
                "list": "users",
                "formatversion": "2",
                "usprop": "groups",
                "ususers": self.user,
            }
            # ---
            data = self.post_params(params)
            # ---
            # _userinfo_ = { "id": 229481, "name": "Mr. Ibrahem", "groups": ["editor", "reviewer", "rollbacker", "*", "user", "autoconfirmed"] }
            # ---
            ff = data.get("query", {}).get("users", [{}])
            # ---
            if ff:
                self.meta.userinfo = ff[0]
        # ---
        return self.meta.userinfo

    def isRedirect(self):
        # ---
        if not self.meta.is_redirect:
            self.get_infos()
        # ---
        return self.meta.is_redirect

    def isDisambiguation(self):
        # ---
        # if the title ends with '(توضيح)' or '(disambiguation)'
        self.meta.is_Disambig = self.title.endswith("(توضيح)") or self.title.endswith("(disambiguation)")
        # ---
        if self.meta.is_Disambig:
            printe.output(f'<<lightred>> page "{self.title}" is Disambiguation / توضيح')
        # ---
        return self.meta.is_Disambig

    def get_categories(self, with_hidden=False):
        # ---
        # if not self.categories_data.categories: self.get_infos()
        if not self.meta.info["done"]:
            self.get_infos()
        # ---
        if with_hidden:
            return self.categories_data.all_categories_with_hidden
        # ---
        return self.categories_data.categories

    def get_hidden_categories(self):
        # ---
        if self.categories_data.categories == {} and self.categories_data.hidden_categories == {}:
            self.get_infos()
        # ---
        return self.categories_data.hidden_categories

    def get_langlinks(self):
        # ---
        if not self.meta.info["done"]:
            self.get_infos()
        # ---
        return self.langlinks

    def get_templates_API(self):
        # ---
        if not self.meta.info["done"]:
            self.get_infos()
        # ---
        return self.template_data.templates_API

    def get_links_here(self):
        # ---
        if not self.meta.info["done"]:
            self.get_infos()
        # ---
        return self.links_data.links_here

    def get_wiki_links_from_text(self):
        if not self.text:
            self.text = self.get_text()
        # ---
        parsed = wtp.parse(self.text)
        wikilinks = parsed.wikilinks
        # ---
        # printe.output(f'wikilinks:{str(wikilinks)}')
        # ---
        # for x in wikilinks:
        #     print(x.title)
        # ---
        return wikilinks

    def Get_tags(self, tag=""):
        if not self.text:
            self.text = self.get_text()
        # ---
        self.text = self.text.replace("<ref>", '<ref name="ss">', 1)
        # ---
        parsed = wtp.parse(self.text)
        tags = parsed.get_tags()
        # ---
        # printe.output(f'tags:{str(tags)}')
        # ---
        if not tag:
            return tags
        # ---
        new_tags = []
        # ---
        for x in tags:
            if x.name == tag:
                new_tags.append(x)
        # ---
        # return tags if tag == '' else [x for x in tags if x.name == tag]
        # ---
        return new_tags

    def can_edit(self, script="", delay=0):
        # ---
        if self.family != "wikipedia":
            return True
        # ---
        if not self.text:
            self.text = self.get_text()
        # ---
        self.meta.can_be_edit = botEdit.bot_May_Edit(text=self.text, title_page=self.title, botjob=script, page=self, delay=delay)
        # ---
        return self.meta.can_be_edit

    def is_flagged(self):
        # ---
        """
        Returns whether the page is flagged for review or quality control.

        If the page text has not been loaded, it is retrieved before checking the flagged status.

        Returns:
            bool: True if the page is flagged, False otherwise.
        """
        if not self.text:
            self.text = self.get_text()
        # ---
        return self.meta.flagged

    def get_create_data(self):
        """
        Returns the page creation metadata, fetching it if not already loaded.

        The creation metadata includes the timestamp, user, and anonymity status of the first revision.
        """
        if not self.meta.create_data:
            self.find_create_data()
        return self.meta.create_data

    def get_timestamp(self):
        """
        Returns the timestamp of the latest revision of the page.

        If the timestamp is not already loaded, retrieves the page content to obtain it.
        """
        if not self.revisions_data.timestamp:
            self.get_text()
        return self.revisions_data.timestamp

    def get_newrevid(self):
        # newrevid is only populated on successful edit/create responses.
        if not self.revisions_data.newrevid:
            # Ensure we at least have the current revid loaded.
            if not self.revisions_data.revid:
                self.get_text()
        # Fallback to current revid if no newrevid exists.
        return self.revisions_data.newrevid or self.revisions_data.revid

    def get_revid(self):
        if not self.revisions_data.revid:
            self.get_text()
        return self.revisions_data.revid

    def exists(self):
        if not self.meta.Exists:
            self.get_text()
        if not self.meta.Exists:
            printe.output(f'page "{self.title}" not exists in {self.lang}:{self.family}')
        return self.meta.Exists

    def namespace(self):
        if self.ns is False:
            self.get_text()
        return self.ns

    def get_user(self):
        if not self.user:
            self.get_text()
        return self.user

    def get_templates(self):
        if not self.text:
            self.text = self.get_text()
        self.template_data.templates = txtlib.extract_templates_and_params(self.text)
        return self.template_data.templates

    def save(self, newtext="", summary="", nocreate=1, minor="0", tags="", nodiff=False, ASK=False):
        """
        Saves new text to the page, updating its content and metadata.

        Prompts for confirmation and checks for invalid edits before submitting the change. Updates instance attributes with the latest revision and timestamps on success.

        Args:
                newtext: The new wikitext to save to the page.
                summary: Edit summary for the change.
                nocreate: If 1 (default), prevents creating the page if it does not exist.
                minor: Indicates if the edit should be marked as minor.
                tags: Optional tags to associate with the edit.
                nodiff: If True, skips showing a diff before saving.
                ASK: If True, prompts the user for confirmation before saving.

        Returns:
                True if the edit was successful, False otherwise.
        """
        # ---
        self.newtext = newtext
        if summary:
            self.content.summary = summary
        # ---
        if self.false_edit():
            return False
        # ---
        message = f"Do you want to save this page? ({self.lang}:{self.title})"
        # ---
        user = self.meta.username or getattr(self, 'user_login', '')
        # ---
        if self.ask_put(nodiff=nodiff, newtext=newtext, text=self.text, message=message, job="save", username=user, summary=self.content.summary) is False:
            return False
        # ---
        params = {
            "action": "edit",
            "title": self.title,
            "text": newtext,
            "summary": self.content.summary,
            "minor": minor,
            "nocreate": nocreate,
        }
        # ---
        if nocreate != 1:
            del params["nocreate"]
        # ---
        if self.revisions_data.revid:
            params["baserevid"] = self.revisions_data.revid
        # ---
        if tags:
            params["tags"] = tags
        # ---
        # params['basetimestamp'] = self.revisions_data.timestamp
        # ---
        pop = self.post_params(params, addtoken=True)
        # ---
        if not pop:
            return False
        # ---
        error = pop.get("error", {})
        edit = pop.get("edit", {})
        result = edit.get("result", "")
        # ---
        # {'edit': {'result': 'Success', 'pageid': 5013, 'title': 'User:Mr. Ibrahem/sandbox', 'contentmodel': 'wikitext', 'oldrevid': 1336986, 'newrevid': 1343447, 'newtimestamp': '2023-04-01T23:14:07Z', 'watched': ''}}
        # ---
        if result.lower() == "success":
            self.text = newtext
            self.user = ""
            printe.output(f"<<lightgreen>> ** true .. [[{self.lang}:{self.family}:{self.title}]] ")
            # printe.output('Done True...')
            # ---
            if "printpop" in sys.argv:
                print(pop)
            # ---
            self.revisions_data.pageid = edit.get("pageid") or self.revisions_data.pageid
            self.revisions_data.revid = edit.get("newrevid") or self.revisions_data.revid
            self.revisions_data.newrevid = edit.get("newrevid") or self.revisions_data.newrevid
            self.revisions_data.touched = edit.get("touched") or self.revisions_data.touched
            self.revisions_data.timestamp = edit.get("newtimestamp") or self.revisions_data.timestamp
            # ---
            return True
        # ---
        if error != {}:
            print(pop)
            er = self.handel_err(error, function="Save", params=params)
            # ---
            return er
        # ---
        return False

    def purge(self):
        # ---
        params = {
            "action": "purge",
            "forcelinkupdate": 1,
            "forcerecursivelinkupdate": 1,
            "titles": self.title,
        }
        # ---
        data = self.post_params(params, addtoken=True)
        # ---
        if not data:
            printe.output("<<lightred>> ** purge error. ")
            return False
        # ---
        title2 = self.title
        # ---
        #  'normalized': [{'from': 'وب:ملعب', 'to': 'ويكيبيديا:ملعب'}]}
        # ---
        for x in data.get("normalized", []):
            # printe.output(f"normalized from {x['from']} to {x['to']}")
            if x["from"] == self.title:
                title2 = x["to"]
                break
        # ---
        for t in data.get("purge", []):
            # t = [{'ns': 4, 'title': 'ويكيبيديا:ملعب', 'purged': '', 'linkupdate': ''}]
            ti = t["title"]
            if title2 == ti and "purged" in t:
                return True
            if "missing" in t:
                printe.output(f"page \"{t['title']}\" missing")
                return "missing"
        return False

    def Create(self, text="", summary="", nodiff="", noask=False):
        # ---
        """
        Creates a new page with the specified text and summary.

        If user confirmation is not suppressed, prompts the user before creating the page. Only succeeds if the page does not already exist. Updates instance attributes with the new page state on success.

        Args:
            text: The wikitext content to use for the new page.
            summary: Edit summary for the page creation.
            nodiff: If set, disables showing a diff before confirmation.
            noask: If True, skips the user confirmation prompt.

        Returns:
            True if the page was created successfully, False otherwise or if the user aborts.
        """
        self.newtext = text
        # ---
        if not noask:
            # ---
            message = f"Do you want to create this page? ({self.lang}:{self.title})"
            # ---
            user = self.meta.username or getattr(self, 'user_login', '')
            # ---
            if self.ask_put(nodiff=nodiff, newtext=text, message=message, job="create", username=user, summary=summary) is False:
                return False
        # ---
        params = {
            "action": "edit",
            "title": self.title,
            "text": text,
            "summary": summary,
            "notminor": 1,
            "createonly": 1,
        }
        # ---
        pop = self.post_params(params, addtoken=True)
        # ---
        if not pop:
            return False
        # ---
        error = pop.get("error", {})
        edit = pop.get("edit", {})
        result = edit.get("result", "")
        # ---
        if print_test[1]:
            print("pop:")
            print(pop)
        # ---
        if result.lower() == "success":
            # ---
            # {'edit': {'new': '', 'result': 'Success', 'pageid': 9090918, 'title': 'مستخدم:Mr. Ibrahem/test2024', 'contentmodel': 'wikitext', 'oldrevid': 0, 'newrevid': 61016221, 'newtimestamp': '2023-02-01T21:52:42Z'}}
            # ---
            self.text = text
            # ---
            printe.output(f"<<lightgreen>> ** true .. [[{self.lang}:{self.family}:{self.title}]] ")
            # printe.output('Done True... time.sleep() ')
            # ---
            self.revisions_data.pageid = edit.get("pageid") or self.revisions_data.pageid
            self.revisions_data.revid = edit.get("newrevid") or self.revisions_data.revid
            self.revisions_data.touched = edit.get("touched") or self.revisions_data.touched
            self.revisions_data.newrevid = edit.get("newrevid") or self.revisions_data.newrevid
            self.revisions_data.timestamp = edit.get("newtimestamp") or self.revisions_data.timestamp
            # ---
            return True
        # ---
        if error != {}:
            print(pop)
            er = self.handel_err(error, function="Create", params=params)
            # ---
            return er
            # ---
        return False

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
        self.links_data.back_links = back_links
        # ---
        return self.links_data.back_links

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
        self.links_data.links2 = data
        # ---
        return self.links_data.links2

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
        self.links_data.links = data
        # ---
        return self.links_data.links

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
        self.revisions_data.revisions = revisions
        # ---
        return revisions
