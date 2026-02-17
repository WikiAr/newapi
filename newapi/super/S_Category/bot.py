"""

from .bot import CategoryDepth

"""

import copy
import logging

import tqdm

logger = logging.getLogger(__name__)

ns_list = {
    "0": "",
    "1": "نقاش",
    "2": "مستخدم",
    "3": "نقاش المستخدم",
    "4": "ويكيبيديا",
    "5": "نقاش ويكيبيديا",
    "6": "ملف",
    "7": "نقاش الملف",
    "10": "قالب",
    "11": "نقاش القالب",
    "12": "مساعدة",
    "13": "نقاش المساعدة",
    "14": "تصنيف",
    "15": "نقاش التصنيف",
    "100": "بوابة",
    "101": "نقاش البوابة",
    "828": "وحدة",
    "829": "نقاش الوحدة",
    "2600": "موضوع",
    "1728": "فعالية",
    "1729": "نقاش الفعالية",
}


class CategoryDepth:
    def __init__(self, login_bot, title, **kwargs):
        # ---
        self.login_bot = login_bot
        # ---
        self.user_login = login_bot.user_login
        # ---
        self.title = title
        # ---
        self.len_pages = 0
        self.revids, self.timestamps, self.result_table = {}, {}, {}
        # ---
        self.props = []
        # ---
        self.gcmlimit = 1000
        self.no_props = False
        self.limit = 0
        self.no_gcmsort = False
        self.only_titles = False
        self.onlyns = False
        self.tempyes = []
        self.without_lang = ""
        self.with_lang = ""
        self.depth = 0
        self.ns = "all"
        self.nslist = []
        # ---
        kwargs["title"] = title
        # ---
        self.prase_params(**kwargs)

    def post_params(
        self,
        params,
        Type="get",
        addtoken=False,
        GET_CSRF=True,
        files=None,
        do_error=False,
        max_retry=0,
    ):
        # ---
        return self.login_bot.post_params(
            params,
            Type=Type,
            addtoken=addtoken,
            GET_CSRF=GET_CSRF,
            files=files,
            do_error=do_error,
            max_retry=max_retry,
        )

    def get_revids(self):
        return self.revids

    def get_len_pages(self):
        return self.len_pages

    def prase_params(self, **kwargs):
        # ---
        if not kwargs:
            return
        # ---
        self.len_pages = 0
        # ---
        self.revids, self.timestamps, self.result_table = {}, {}, {}
        # ---
        self.title = kwargs.get("title")
        # ---
        if not isinstance(self.depth, int):
            try:
                self.depth = int(self.depth)
            except ValueError:
                print(f"self.depth != int: {self.depth}")
                self.depth = 0
        # ---
        self.props = []
        # ---
        if isinstance(kwargs.get("props"), str):
            self.props = [kwargs.get("props")]
        # ---
        self.gcmlimit = kwargs.get("gcmlimit") or 1000
        self.no_props = kwargs.get("no_props") or False
        # ---
        self.limit = kwargs.get("limit") or 0
        # ---
        self.no_gcmsort = kwargs.get("no_gcmsort") or False
        # ---
        self.only_titles = kwargs.get("only_titles") or False
        self.onlyns = kwargs.get("onlyns") or False
        self.tempyes = kwargs.get("tempyes") or []

        self.without_lang = kwargs.get("without_lang") or ""
        self.with_lang = kwargs.get("with_lang") or ""

        self.depth = kwargs.get("depth") or 0
        self.ns = kwargs.get("ns") or "all"
        self.ns = str(self.ns)
        self.nslist = kwargs.get("nslist") or []

    def Login_to_wiki(self):
        self.log_to_wiki_1()
        return

    def params_work(self, params):
        t_props = ["revisions"] if not self.no_gcmsort else []
        # ---
        if self.no_props:
            t_props = []
        # ---
        if self.no_gcmsort:
            del params["gcmsort"]
            del params["gcmdir"]
        # ---
        if self.tempyes != []:
            t_props.append("templates")
            params["tllimit"] = "max"
            params["tltemplates"] = "|".join(self.tempyes)
        # ---
        if self.with_lang or self.without_lang:  # مع وصلة لغة معينة
            t_props.append("langlinks")
            params["lllimit"] = "max"
        # ---
        if self.ns in ["0", "10"]:
            params["gcmtype"] = "page"
        elif self.ns in [14]:
            params["gcmtype"] = "subcat"
        # ---
        # print('gcmtype::', params["gcmtype"])
        # ---
        if len(self.nslist) > 0:
            if self.nslist == [14]:
                params["gcmtype"] = "subcat"
            elif 14 not in self.nslist and self.depth == 0:
                params["gcmtype"] = "page"
        # ---
        # print('gcmtype::', params["gcmtype"])
        # ---
        if not self.no_props:
            for x in self.props:
                if x not in t_props:
                    t_props.append(x)
            # ---
            if len(t_props) > 0:
                params["prop"] = "|".join(t_props)
            # ---
            if "categories" in params["prop"]:
                # params["clprop"] = "hidden"
                params["cllimit"] = "max"
            # ---
            if "revisions" in params["prop"]:
                params["rvprop"] = "timestamp|ids"
        # ---
        return params

    def pages_table_work(self, table, pages):
        # ---
        self.len_pages += len(pages)
        # ---
        for category in pages:
            caca = pages[category] if isinstance(pages, dict) else category
            cate_title = caca["title"]
            # ---
            timestamp = caca.get("revisions", [{}])[0].get("timestamp", "")
            self.timestamps[cate_title] = timestamp
            # ---
            revid = caca.get("revisions", [{}])[0].get("revid", "")
            self.revids[cate_title] = revid
            # ---
            p_ns = str(caca.get("ns", 0))
            # ---
            tablese = table.get(cate_title, {})
            if revid:
                tablese["revid"] = revid
            # ---
            if p_ns:
                tablese["ns"] = caca["ns"]
                # ---
                if self.ns == "14" or self.nslist == [14]:
                    if p_ns != "14":
                        continue
                # ---
                if self.ns == "0" or self.nslist == [0]:
                    if p_ns != "0":
                        continue
                # ---
                # do same for ns_list
                # if self.ns in ns_list:
                #     if p_ns not in ns_list:
                #         continue
            # ---
            templates = [x["title"] for x in caca.get("templates", {})]
            # ---
            if templates:
                if tablese.get("templates"):
                    tablese["templates"].extend(templates)
                else:
                    tablese["templates"] = templates
                # ---
                tablese["templates"] = list(set(tablese["templates"]))
            # ---
            langlinks = {fo["lang"]: fo.get("title") or fo.get("*") or "" for fo in caca.get("langlinks", [])}
            # ---
            if langlinks:
                if tablese.get("langlinks"):
                    tablese["langlinks"].update(langlinks)
                else:
                    tablese["langlinks"] = langlinks
            # ---
            # categories = {x["title"]: x for x in caca.get("categories", {})}
            categories = [x["title"] for x in caca.get("categories", {})]
            # ---
            if categories:
                if tablese.get("categories"):
                    tablese["categories"].extend(categories)
                else:
                    tablese["categories"] = categories
            # ---
            table[cate_title] = tablese
        # ---
        return table

    def get_cat_new(self, cac):
        # ---
        # print("get_cat_new")
        # ---
        params = {
            "action": "query",
            "format": "json",
            "utf8": 1,
            "generator": "categorymembers",
            "gcmprop": "title",
            # "prop": "revisions",
            "gcmtype": "page|subcat",
            "gcmlimit": self.gcmlimit,
            "formatversion": "1",
            "gcmsort": "timestamp",
            "gcmdir": "newer",
            # "rvprop": "timestamp",
        }
        # ---
        params = self.params_work(params)
        # ---
        params["gcmtitle"] = cac
        params["action"] = "query"
        # ---
        results = {}
        # ---
        continue_params = {}
        # ---
        d = 0
        # ---
        while continue_params != {} or d == 0:
            # ---
            d += 1
            # ---
            if self.limit > 0 and len(results) >= self.limit:
                logger.info(f"<<yellow>> limit:{self.limit} reached, len of results: {len(results)} break ..")
                break
            # ---
            if continue_params:
                # params = {**params, **continue_params}
                params.update(continue_params)
            # ---
            api_data = self.post_params(params)
            # ---
            if not api_data:
                print(f"api is False for {cac}")
                break
            # ---
            continue_params = api_data.get("continue", {})
            # ---
            pages = api_data.get("query", {}).get("pages", {})
            # ---
            results = self.pages_table_work(results, pages)
        # ---
        return results

    def add_to_result_table(self, x, tab):
        if self.without_lang:
            no_langs = tab.get("langlinks", {}).get(self.without_lang, "")
            if no_langs:
                return

        if self.with_lang:
            langs = tab.get("langlinks", {}).get(self.with_lang, "")
            if not langs:
                return

        if self.onlyns:
            p_ns = str(tab.get("ns", 0))
            if p_ns != str(self.onlyns):
                return
        # ---
        if self.only_titles:
            self.result_table.setdefault(x, {})
            return
        # ---
        # print(tab)
        if x in self.result_table:
            tab2 = copy.deepcopy(self.result_table[x])
            tab2.update(tab)
            tab = tab2
        # ---
        self.result_table[x] = tab

    def subcatquery_(self, **kwargs):
        # ---
        # self.prase_params(**kwargs)
        # ---
        tablemember = self.get_cat_new(self.title)
        # ---
        for x, zz in tablemember.items():
            self.add_to_result_table(x, zz)
        # ---
        new_list = [x for x, xx in tablemember.items() if int(xx["ns"]) == 14]
        # ---
        depth_done = 0
        # ---
        while self.depth > depth_done:
            new_tab2 = []
            # ---
            if self.limit > 0 and len(self.result_table) >= self.limit:
                logger.info(f"<<yellow>> limit:{self.limit} reached, len of results: {len(self.result_table)} break ..")
                break
            # ---
            depth_done += 1
            # ---
            # logger.info(f"<<yellow>> work in subcats: {len(new_list)}, depth:{depth_done}/{self.depth}:")
            # ---
            for cat in tqdm.tqdm(new_list):
                # ---
                table2 = self.get_cat_new(cat)
                # ---
                for x, v in table2.items():
                    # ---
                    if int(v["ns"]) == 14:
                        new_tab2.append(x)
                    # ---
                    self.add_to_result_table(x, v)
            # ---
            new_list = new_tab2
        # ---
        # sort self.result_table by timestamp
        if not self.no_gcmsort:
            soro = sorted(
                self.result_table.items(),
                key=lambda item: self.timestamps.get(item[0], 0),
                reverse=True,
            )
            self.result_table = {k: v for k, v in soro}
        # ---
        return self.result_table
