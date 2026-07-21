""" """

from __future__ import annotations

import copy
import logging
from typing import Any

from tqdm import tqdm

from ...api_client import WikiLoginClient

logger = logging.getLogger(__name__)


class CategoryDepth:
    """
    Class for traversing category hierarchies.

    Provides methods for recursively querying category members.
    """

    def __init__(
        self,
        login_bot: WikiLoginClient,
        title: str = "",
        **kwargs,
    ) -> None:
        self.login_bot = login_bot

        self.title: str = title

        self.len_pages: int = 0
        self.revids: dict = {}
        self.timestamps: dict = {}
        self.result_table: dict[str, dict] = {}

        self.props: list = []

        self.gcmlimit: int = 1000
        self.no_props: bool = False
        self.limit: int = 0
        self.no_gcm_sort: bool = False
        self.only_titles: bool = False
        self.onlyns: bool = False
        self.template_whitelist: list = []
        self.without_lang: str = ""
        self.with_lang: str = ""
        self.gcmtype: str = ""
        self.depth: int = 0
        self.ns: str = "all"
        self.nslist: list = []

        kwargs["title"] = title
        self._parse_params(**kwargs)

    def get_revids(self) -> dict[str, int]:
        return self.revids

    def get_len_pages(self) -> int:
        return self.len_pages

    def _parse_params(self, **kwargs) -> None:
        if not kwargs:
            return

        self.len_pages = 0
        self.revids, self.timestamps = {}, {}
        self.result_table: dict[str, dict] = {}

        self.title = kwargs.get("title", "")
        logger.debug(f"parsing params for {self.title}: depth={kwargs.get('depth')}, ns={kwargs.get('ns')}")

        try:
            self.depth = int(kwargs.get("depth", 0))
        except ValueError:
            logger.error(f"self.depth != int: {kwargs.get('depth')}")
            self.depth = 0

        self.props: list = []
        if isinstance(kwargs.get("props"), str):
            self.props = [kwargs.get("props")]

        self.gcmtype = kwargs.get("gcmtype") or ""
        self.gcmlimit = kwargs.get("gcmlimit") or 1000
        self.no_props = kwargs.get("no_props") or False

        self.limit = kwargs.get("limit") or 0
        self.no_gcm_sort = kwargs.get("no_gcmsort") or False

        self.only_titles = kwargs.get("only_titles") or False
        self.onlyns = kwargs.get("onlyns") or False
        self.template_whitelist = kwargs.get("tempyes") or []

        self.without_lang = kwargs.get("without_lang") or ""
        self.with_lang = kwargs.get("with_lang") or ""

        self.ns = str(kwargs.get("ns") or "all")
        self.nslist = kwargs.get("nslist") or []

    def _determine_gcmtype(self, params: dict) -> dict:
        if self.no_gcm_sort:
            del params["gcmsort"]
            del params["gcmdir"]
        return params

    def _build_prop_list(self) -> list:
        t_props = ["revisions"] if not self.no_gcm_sort else []

        if self.no_props:
            t_props: list = []

        if self.template_whitelist:
            t_props.append("templates")

        if self.with_lang or self.without_lang:
            t_props.append("langlinks")

        return t_props

    def params_work(self, params: dict) -> dict:
        t_props = self._build_prop_list()

        params = self._determine_gcmtype(params)

        if self.template_whitelist:
            params["tllimit"] = "max"
            params["tltemplates"] = "|".join(self.template_whitelist)

        if self.with_lang or self.without_lang:
            params["lllimit"] = "max"

        if self.gcmtype:
            params["gcmtype"] = self.gcmtype

        if self.ns in ["0", "10"]:
            params["gcmtype"] = "page"
        elif int(self.ns) in [14]:
            params["gcmtype"] = "subcat"

        if self.nslist == [14]:
            params["gcmtype"] = "subcat"
        elif 14 not in self.nslist and self.depth == 0:
            params["gcmtype"] = "page"

        if not self.no_props:
            for x in self.props:
                if x not in t_props:
                    t_props.append(x)

            if t_props:
                params["prop"] = "|".join(t_props)

            if "categories" in params.get("prop", ""):
                # params["clprop"] = "hidden"
                params["cllimit"] = "max"

            if "revisions" in params.get("prop", ""):
                params["rvprop"] = "timestamp|ids"

        return params

    def _extract_timestamp_revid(self, caca: dict) -> tuple:
        timestamp = caca.get("revisions", [{}])[0].get("timestamp", "")
        revid = caca.get("revisions", [{}])[0].get("revid", "")
        return timestamp, revid

    def _filter_by_namespace(self, p_ns: str) -> bool:
        if self.ns == "14" or self.nslist == [14]:
            if p_ns != "14":
                return False
        if self.ns == "0" or self.nslist == [0]:
            if p_ns != "0":
                return False
        return True

    def _merge_templates(self, tablese: dict, caca: dict) -> None:
        templates = [x["title"] for x in caca.get("templates", {})]
        if templates:
            if tablese.get("templates"):
                tablese["templates"].extend(templates)
            else:
                tablese["templates"] = templates
            tablese["templates"] = list(set(tablese["templates"]))

    def _merge_langlinks(self, tablese: dict, caca: dict) -> None:
        langlinks = {fo["lang"]: fo.get("title") or fo.get("*") or "" for fo in caca.get("langlinks", [])}
        if langlinks:
            if tablese.get("langlinks"):
                tablese["langlinks"].update(langlinks)
            else:
                tablese["langlinks"] = langlinks

    def _merge_categories(self, tablese: dict, caca: dict) -> None:
        categories = [x["title"] for x in caca.get("categories", {})]
        if categories:
            if tablese.get("categories"):
                tablese["categories"].extend(categories)
            else:
                tablese["categories"] = categories

    def pages_table_work(self, results: dict, pages: list[dict[str, Any]]) -> dict:
        self.len_pages += len(pages)

        for item_data in pages:
            # item_data exampe: { "pageid": 350939, "ns": 0, "title": "Yemen", "langlinks": [ { "lang": "ar", "title": "اليمن" } ] }
            cate_title = item_data["title"]

            timestamp, revid = self._extract_timestamp_revid(item_data)
            self.timestamps[cate_title] = timestamp
            self.revids[cate_title] = revid

            p_ns = str(item_data.get("ns", 0))

            tablese = results.get(cate_title, {})
            if revid:
                tablese["revid"] = revid

            if p_ns:
                tablese["ns"] = item_data["ns"]
                if not self._filter_by_namespace(p_ns):
                    continue

            self._merge_templates(tablese, item_data)
            self._merge_langlinks(tablese, item_data)
            self._merge_categories(tablese, item_data)

            results[cate_title] = tablese

        return results

    def get_cat_new(self, cac: str) -> dict:
        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "utf8": 1,
            "generator": "categorymembers",
            "gcmprop": "title",
            "gcmtype": "page|subcat",
            "gcmlimit": self.gcmlimit,
            "formatversion": "1",
            "gcmsort": "timestamp",
            "gcmdir": "newer",
        }

        params = self.params_work(params)
        params["gcmtitle"] = cac
        params["action"] = "query"

        results = {}
        continue_params = {}

        while True:
            if self.limit > 0 and len(results) >= self.limit:
                logger.debug(f"<<yellow>> limit:{self.limit} reached, len of results: {len(results)} break ..")
                break

            if continue_params:
                params.update(continue_params)

            api_data = self.login_bot.client_request_safe(params, method="get")

            if not api_data:
                logger.info(f"api is False for {cac}")
                break

            continue_params = api_data.get("continue", {})
            pages: list[dict[str, Any]] = api_data.get("query", {}).get("pages") or []
            results = self.pages_table_work(results, pages)

            if not continue_params:
                break

        return results

    def add_to_result_table(self, x: str, tab: dict) -> None:
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

        if self.only_titles:
            self.result_table.setdefault(x, {})
            return

        if x in self.result_table:
            tab2 = copy.deepcopy(self.result_table[x])
            tab2.update(tab)
            tab = tab2

        self.result_table[x] = tab

    def subcatquery_(self) -> dict[str, dict]:
        logger.debug(f"starting subcatquery for {self.title}, depth={self.depth}")
        tablemember = self.get_cat_new(self.title)

        for x, zz in tablemember.items():
            self.add_to_result_table(x, zz)

        new_list = [x for x, xx in tablemember.items() if int(xx["ns"]) == 14]

        depth_done = 0

        while self.depth > depth_done:
            new_tab2: list = []

            if self.limit > 0 and len(self.result_table) >= self.limit:
                logger.debug(
                    f"<<yellow>> limit:{self.limit} reached, len of results: {len(self.result_table)} break .."
                )
                break

            depth_done += 1
            logger.debug(f"depth {depth_done}/{self.depth}: {len(new_list)} subcategories to process")

            for cat in tqdm(new_list):
                table2 = self.get_cat_new(cat)

                for x, v in table2.items():
                    if int(v["ns"]) == 14:
                        new_tab2.append(x)
                    self.add_to_result_table(x, v)

            new_list = new_tab2

        if not self.no_gcm_sort:
            soro = sorted(self.result_table.items(), key=lambda item: self.timestamps.get(item[0], 0), reverse=True)
            self.result_table = dict(soro)

        logger.info(f"{self.title=}, {self.depth}, {len(self.result_table)} total results")
        return self.result_table


__all__ = [
    "CategoryDepth",
]
