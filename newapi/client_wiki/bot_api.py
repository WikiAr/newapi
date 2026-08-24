""" """

from __future__ import annotations

import datetime
import logging
import sys
from collections.abc import KeysView
from datetime import timedelta
from typing import Any

from ..api_client import WikiLoginClient
from .api_utils import change_codes
from .api_utils.ask_bot import AskBot
from .api_utils.handel_errors import HandleErrors

logger = logging.getLogger(__name__)


class NewApiHelpers:
    def __init__(self) -> None:
        pass

    def chunk_titles(self, titles: Any, chunk_size: int = 50):
        # ---
        if isinstance(titles, dict):
            titles = list(titles.keys())

        elif isinstance(titles, KeysView):
            # TypeError: 'dict_keys' object is not subscriptable
            titles = list(titles)
        # ---
        result = [titles[i : i + chunk_size] for i in range(0, len(titles), chunk_size)]
        # ---
        return result


class NewApi(NewApiHelpers):
    def __init__(
        self,
        login_bot: WikiLoginClient,
        lang: str = "",
        family: str = "wikipedia",
    ) -> None:
        # ---
        self.error_handler = HandleErrors()
        self.login_bot = login_bot
        # ---
        self.username = getattr(self, "username", "")
        self.lang = change_codes.get(lang) or lang
        # ---
        self.ask_bot = AskBot(
            ask="ask" in sys.argv,
            nodiff="nodiff" in sys.argv,
        )
        # ---
        super().__init__()

    def get_username(self):
        return self.username

    def find_pages_exists_or_not(
        self,
        liste,
        get_redirect: bool = False,
        chunk_size: int = 50,
    ) -> dict[str, Any]:
        # ---
        done = 0
        # ---
        pages_table: list = []
        normalized_table: list = []
        # ---
        # ---
        for titles in self.chunk_titles(liste, chunk_size=chunk_size):
            # ---
            done += len(titles)
            # ---
            params: dict[str, Any] = {
                "action": "query",
                "titles": "|".join(titles),
                "prop": "info|pageprops",
                "ppprop": "wikibase_item",
                "formatversion": 2,
            }
            # ---
            json1 = self.login_bot.client_request_safe(params, method="post")
            # ---
            if not json1:
                continue
            # ---
            query = json1.get("query", {})
            # ---
            pages_table.extend(query.get("pages", []))
            normalized_table.extend(query.get("normalized", []))
        # ---
        redirects = 0
        missing = 0
        exists = 0
        # ---
        normalized = {red["to"]: red["from"] for red in normalized_table}
        # ---
        table = {}
        # ---
        for kk in pages_table:
            # ---
            if isinstance(pages_table, dict):
                kk = pages_table[kk]
            # ---
            title_x = kk.get("title", "")
            # ---
            if not title_x:
                continue
            # ---
            title_x = normalized.get(title_x, title_x)
            # ---
            table[title_x] = True
            # ---
            if "missing" in kk:
                table[title_x] = False
                missing += 1
            elif "redirect" in kk and get_redirect:
                table[title_x] = "redirect"
                redirects += 1
            else:
                exists += 1
        # ---
        logger.debug(f"find_pages_exists_or_not : missing:{missing}, exists: {exists}, redirects: {redirects}")
        # ---
        return table

    def find_pages_exists_or_not_with_qids(
        self,
        liste,
        get_redirect: bool = False,
        return_all_jsons: bool = False,
        use_user_input_title: bool = False,
        chunk_size: int = 50,
    ) -> dict | tuple[dict, dict]:
        # ---
        done = 0
        # ---
        pages_table: list = []
        normalized_table: list[dict[str, dict]] = []
        redirects_table: list[dict[str, dict]] = []
        # ---
        all_jsons = {}
        # ---
        for titles in self.chunk_titles(liste, chunk_size=chunk_size):
            # ---
            done += len(titles)
            # ---
            params: dict[str, Any] = {
                "action": "query",
                "titles": "|".join(titles),
                "prop": "info|pageprops",
                "ppprop": "wikibase_item",
                "pplimit": "max",
                "formatversion": 2,
                "converttitles": 1,
            }
            # ---
            if get_redirect:
                params["redirects"] = 1
            # ---
            json1 = self.login_bot.client_request_safe(params, method="post")
            # ---
            if not json1:
                continue
            # ---
            query = json1.get("query", {})
            # ---
            pages_table.extend(query.get("pages", []))
            normalized_table.extend(query.get("normalized", []))
            redirects_table.extend(query.get("redirects", []))
        # ---
        redirects = 0
        missing = 0
        exists = 0
        # ---
        table = {}
        # ---
        for kk in pages_table:
            # ---
            if isinstance(pages_table, dict):
                kk = pages_table[kk]
            # ---
            wikibase_item = kk.get("pageprops", {}).get("wikibase_item", "")
            # ---
            title_x = kk.get("title", "")
            # ---
            if not title_x:
                continue
            # ---
            title_tab = self._get_title_redirect_normalize(title_x, redirects_table, normalized_table)
            # ---
            if use_user_input_title and title_tab.get("user_input"):
                title_x = title_tab["user_input"]
            # ---
            table.setdefault(title_x, {"wikibase_item": wikibase_item, "exist": False})
            # ---
            if title_tab:
                table[title_x]["title_tab"] = title_tab
            # ---
            if wikibase_item:
                table[title_x]["wikibase_item"] = wikibase_item
            # ---
            if "missing" in kk:
                table[title_x]["exist"] = False
                missing += 1
            elif title_x == title_tab.get("redirect_to", ""):
                table[title_x]["exist"] = "redirect"
                table[title_x]["redirect"] = True
                redirects += 1
            else:
                table[title_x]["exist"] = True
                exists += 1
        # ---
        logger.debug(f"find_pages_exists_or_not : missing:{missing}, exists: {exists}, redirects: {redirects}")
        # ---
        if return_all_jsons:
            return table, all_jsons
        # ---
        return table

    def get_all_pages(
        self,
        start: str = "",
        namespace: str = "0",
        limit: int | str = "max",
        apfilterredir: str = "",
        ppprop: str = "",
        limit_all: int = 100000,
    ) -> list[str]:
        # ---
        logger.debug(
            f"get_all_pages for start:{start}, limit:{limit},namespace:{namespace},apfilterredir:{apfilterredir}"
        )
        # ---
        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "prop": "pageprops",
            "list": "allpages",
            "apnamespace": namespace,
            "aplimit": limit,
            "apfilterredir": "nonredirects",
            "formatversion": 1,
        }
        # ---
        if str(namespace) in ["*", "", "all"]:
            params.pop("apnamespace", None)
        # ---
        if ppprop:
            params["ppprop"] = ppprop
        # ---
        if apfilterredir in ["redirects", "all", "nonredirects"]:
            params["apfilterredir"] = apfilterredir
        # ---
        if start:
            params["apfrom"] = start

        # ---
        def _load_data(body):
            return body.get("query", {}).get("allpages") or []

        newp = self.login_bot.post_continue_list(
            params=params,
            action="query",
            max=limit_all,
            _load_data=_load_data,
        )
        # ---
        logger.debug(f"<<lightpurple>> --- : find {len(newp)} pages.")
        # ---
        Main_table = [x["title"] for x in newp]
        # ---
        logger.debug(f"len of Main_table {len(Main_table)}.")
        # ---
        logger.info(f"bot_api.py : find {len(Main_table)} pages.")
        # ---
        return Main_table

    def get_all_pages_generator(
        self,
        start: str = "",
        namespace: str = "0",
        limit: int | str = "max",
        filterredir: str = "",
        ppprop: str = "",
        limit_all: int = 100000,
    ):
        # ---
        logger.debug(
            f"get_all_pages_generator for start:{start}, limit:{limit},namespace:{namespace},filterredir:{filterredir}"
        )
        # ---
        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "prop": "pageprops",
            "generator": "allpages",
            "gapnamespace": namespace,
            "gaplimit": limit,
            "formatversion": 2,
            # "ppprop": "unlinkedwikibase_id",
            "utf8": 1,
        }
        # ---
        if str(namespace) in ["*", "", "all"]:
            del params["gapnamespace"]
        # ---
        if ppprop:
            params["ppprop"] = ppprop
        # ---
        if filterredir in ["redirects", "all", "nonredirects"]:
            params["gapfilterredir"] = filterredir
        # ---
        if start:
            params["gapfrom"] = start

        # ---
        def _load_data(body):
            return body.get("query", {}).get("pages") or []

        # ---
        newp = self.login_bot.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
            max=limit_all,
        )
        # ---
        logger.debug(f"<<lightpurple>> --- get_all_pages_generator : find {len(newp)} pages.")
        # ---
        Main_table = {x["title"]: x for x in newp}
        # ---
        logger.debug(f"len of Main_table {len(Main_table)}.")
        # ---
        logger.info(f"bot_api.py get_all_pages_generator : find {len(Main_table)} pages.")
        # ---
        return Main_table

    def prefixsearch(
        self,
        pssearch: str = "",
        ns: str = "0",
        pslimit: str = "max",
        limit_all: int = 100000,
    ) -> list:
        """Perform a prefix search for titles in a specified namespace.

        This function constructs a query to search for titles that start with a
        given prefix. It allows for filtering by namespace and limits the number
        of results returned. The function handles various input formats for the
        namespace and limit parameters, ensuring that the query is properly
        formatted before sending it to the API. The results are then processed
        and returned as a list of titles.

        Args:
            pssearch (str): The prefix string to search for. Defaults to an empty string.
            ns (str): The namespace to search within. Can be "0", "*", "", or "all". Defaults
                to "0".
            pslimit (str): The maximum number of results to return. Defaults to "max".
            limit_all (int): The maximum number of pages to retrieve. Defaults to 100000.

        Returns:
            list: A list of titles that match the prefix search.
        """
        # ---
        logger.debug(f" for start:{pssearch}, pslimit:{pslimit}, ns:{ns}")
        # ---
        pssearch = pssearch.strip() if pssearch else ""
        # ---
        if not pssearch:
            return []
        # ---
        params: dict[str, Any] = {
            "action": "query",
            "list": "prefixsearch",
            "pssearch": pssearch,
            "psnamespace": "*",
            "pslimit": "max",
            "formatversion": "1",
            "format": "json",
        }
        # ---
        if str(ns) in ["*", "", "all"]:
            del params["apnamespace"]
        # ---
        if str(ns).isdigit():
            params["psnamespace"] = ns
        # ---
        if str(pslimit).isdigit():
            params["pslimit"] = pslimit

        # ---
        def _load_data(body):
            return body.get("query", {}).get("prefixsearch") or []

        # ---
        newp = self.login_bot.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
            max=limit_all,
        )
        # ---
        logger.debug(f"<<lightpurple>> --- : find {len(newp)} pages.")
        # ---
        Main_table = [x["title"] for x in newp]
        # ---
        logger.debug(f"len of Main_table {len(Main_table)}.")
        # ---
        logger.info(f"bot_api.py : find {len(Main_table)} pages.")
        # ---
        return Main_table

    def api_search(
        self,
        value: str = "",
        ns: str = "*",
        offset: int | str = "",
        srlimit: str = "max",
        addparams=None,
    ) -> list[dict[str, Any]]:
        # ---
        logger.debug(f'bot_api. for "{value}",ns:{ns}')
        # ---
        if not srlimit:
            srlimit = "max"
        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": value,
            "srnamespace": 0,
            "srlimit": srlimit,
            "formatversion": 1,
        }

        if ns:
            params["srnamespace"] = ns

        if offset:
            params["sroffset"] = offset

        if addparams:
            addparams = {x: v for x, v in addparams.items() if v and x not in params}
            params: dict[str, Any] = {**params, **addparams}

        def _load_data(body):
            return body.get("query", {}).get("search") or []

        search = self.login_bot.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
        )
        results: list = []
        for pag in search:
            # results.append(pag["title"])
            results.append(pag)
        # ---
        logger.debug(f'bot_api. find "{len(search)}" all result: {len(results)}')
        # ---
        return results

    def get_newpages(
        self,
        limit: int | str = 5000,
        namespace: str = "0",
        rcstart: str = "",
        user: str = "",
        three_houers: bool = False,
        offset_minutes: int | str | None = None,
        offset_hours: bool = False,
    ) -> list[str]:
        if three_houers:
            dd = datetime.datetime.now(datetime.UTC) - timedelta(hours=3)
            rcstart = dd.strftime("%Y-%m-%dT%H:%M:00.000Z")

        elif offset_minutes and isinstance(offset_minutes, int):
            dd = datetime.datetime.now(datetime.UTC) - timedelta(minutes=offset_minutes or 0)
            rcstart = dd.strftime("%Y-%m-%dT%H:%M:00.000Z")

        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "list": "recentchanges",
            "rcnamespace": namespace,
            "rclimit": "max",
            "utf8": 1,
            "rctype": "new",
            "formatversion": 2,
        }

        if rcstart:
            params["rcstart"] = rcstart
        if user:
            params["rcuser"] = user

        if (isinstance(limit, str) and limit.isdigit()) or isinstance(limit, int):
            limit = int(limit)
            params["rclimit"] = limit
        else:
            limit = 5000

        def _load_data(body):
            return body.get("query", {}).get("recentchanges") or []

        # ---
        json1 = self.login_bot.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
            max=limit,
        )
        Main_table = [x["title"] for x in json1]

        logger.debug(f'bot_api. find "{len(Main_table)}" result. s')

        return Main_table

    def user_contribs(
        self,
        user,
        limit: int | str = 5000,
        namespace: str = "*",
        ucshow: str = "",
    ) -> list[Any]:
        # ---
        if not limit or limit == 0:
            limit = 5000
        # ---
        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "list": "usercontribs",
            "ucdir": "older",
            "ucnamespace": namespace,
            "uclimit": "max",
            "ucuser": user,
            "utf8": 1,
            # "bot": 1,
            "ucprop": "title",
            "formatversion": 1,
        }
        # ---
        if ucshow:
            params["ucshow"] = ucshow

        # ---
        def _load_data(body):
            return body.get("query", {}).get("usercontribs") or []

        # ---
        results_data = self.login_bot.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
            max=limit,
        )
        # ---
        results = [x["title"] for x in results_data]
        # ---
        return results

    def get_langlinks_for_list(
        self,
        titles: list[str],
        targtsitecode: str = "",
        numbes: int = 40,
    ) -> dict[str, Any]:
        """Retrieve language links for a list of titles from a specified target
        site.

        This function takes a list of titles and queries a media wiki API to
        fetch language links associated with those titles. It handles the
        chunking of titles to comply with API limits and normalizes the results
        to ensure consistency in title representation. The function also allows
        for specifying a target site code to filter the language links returned.

        Args:
            titles (list): A list of titles for which to retrieve language links.
            targtsitecode (str?): The target site code to filter language links.
                Defaults to an empty string.
            numbes (int?): The number of titles to process in each API call.
                Defaults to 40.

        Returns:
            dict: A dictionary where keys are titles and values are dictionaries of
                language links associated with those titles.
        """

        # ---
        logger.debug(f'bot_api.get_langlinks_for_list for "{len(titles)} pages". in wiki:{self.lang}')
        # ---
        targtsitecode = targtsitecode.removesuffix("wiki")
        # ---
        #  error: {'code': 'toomanyvalues', 'info': 'Too many values supplied for parameter "titles". The limit is 50.', 'parameter': 'titles', 'limit': 50, 'lowlimit': 50, 'highlimit': 500, '*': ''}
        # if self.lang != "ar":
        # ---
        numbes = 50
        # ---
        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "prop": "langlinks",
            # "redirects":1,
            # "normalize": 1,
            "lllimit": "max",
            "utf8": 1,
            "formatversion": 1,
        }
        # ---
        if targtsitecode:
            params["lllang"] = targtsitecode
            logger.debug(f'params["lllang"] = {targtsitecode}')
        # ---
        find_targtsitecode = 0
        normalized = {}
        table = {}
        # ---
        for title_chunk in self.chunk_titles(titles, chunk_size=numbes):
            params["titles"] = "|".join(title_chunk)
            # ---
            # logger.debug(f'work for {len(group)} pages')
            # ---
            json1 = self.login_bot.client_request_safe(params, method="post")
            # ---
            if not json1:
                logger.info("bot_api. json1 is empty")
                continue
            # ---
            _error = json1.get("error", {})
            # ---
            # print("json1:")
            # print(json1)
            # ---
            norma = json1.get("query", {}).get("normalized", {})
            # ---
            for red in norma:
                normalized[red["to"]] = red["from"]
            # ---
            query_pages = json1.get("query", {}).get("pages", {})
            # ---
            for _, kk in query_pages.items():
                titlle = kk.get("title", "")
                # ---
                titlle = normalized.get(titlle, titlle)
                # ---
                table[titlle] = {}
                # ---
                for lang in kk.get("langlinks", []):
                    table[titlle][lang["lang"]] = lang["*"]
                    # ---
                    if lang["lang"] == targtsitecode:
                        find_targtsitecode += 1
        # ---
        logger.info(
            f'bot_api.get_langlinks_for_list find "{len(table)}" in table,find_targtsitecode:{targtsitecode}:{find_targtsitecode}'
        )
        # ---
        return table

    def get_logs(self, title: str) -> list:
        # ---
        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "list": "logevents",
            "ledir": "newer",
            "letitle": title,
            "formatversion": 2,
        }
        # ---
        data = self.login_bot.client_request_safe(params, method="post")
        # ---
        if not data:
            return []
        # ---
        logevents = data.get("query", {}).get("logevents") or []
        # ---
        return logevents

    def get_extlinks(self, title: str):
        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "prop": "extlinks",
            "titles": title,
            "utf8": 1,
            "ellimit": "max",
            "formatversion": 2,
        }

        # ---
        def _load_data(body):
            data = body.get("query", {}).get("pages") or []
            if isinstance(data, list) and data:
                data = data[0]
                data = data.get("extlinks", [])
            return data

        # ---
        results = self.login_bot.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
        )
        # ---
        links = [x["url"] for x in results]
        # ---
        return sorted(set(links))

    def get_page_assessments(self, titles_list: str | list[str]) -> list[Any]:

        titles = "|".join(titles_list) if isinstance(titles_list, list) else titles_list
        # ---
        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "prop": "pageassessments",
            "titles": titles,
            "utf8": 1,
            "ellimit": "max",
            "formatversion": 2,
        }

        def _load_data(body):
            return body.get("query", {}).get("pages") or []

        results = self.login_bot.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
        )
        return results

    def get_revisions(
        self,
        title: str,
        rvprop: str = "comment|timestamp|user|content|ids",
        options=None,
    ) -> list[Any]:
        # ---
        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": title,
            "utf8": 1,
            "rvprop": "comment|timestamp|user|content|ids",
            "rvdir": "newer",
            "rvlimit": "max",
            "formatversion": 2,
        }
        # ---
        params["rvprop"] = rvprop or "comment|timestamp|user|content|ids"
        # ---
        if options:
            params.update(options)

        # ---
        def _load_data(body):
            return body.get("query", {}).get("pages") or []

        # ---
        results = self.login_bot.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
        )
        # ---
        return results

    def querypage_list(
        self,
        qppage: str = "Wantedcategories",
        qplimit=None,
        max=None,
    ) -> list[Any]:
        # ---
        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "list": "querypage",
            # "qppage": "Wantedcategories",
            "qplimit": "max",
            "formatversion": 2,
        }
        # ---
        if qplimit and str(qplimit).isdigit():
            params["qplimit"] = qplimit
        # ---
        params["qppage"] = qppage
        # ---
        qppage_values = [
            "Ancientpages",
            "BrokenRedirects",
            "Deadendpages",
            "DisambiguationPageLinks",
            "DisambiguationPages",
            "DoubleRedirects",
            "Fewestrevisions",
            "GadgetUsage",
            "GloballyWantedFiles",
            "ListDuplicatedFiles",
            "Listredirects",
            "Lonelypages",
            "Longpages",
            "MediaStatistics",
            "MostGloballyLinkedFiles",
            "Mostcategories",
            "Mostimages",
            "Mostinterwikis",
            "Mostlinked",
            "Mostlinkedcategories",
            "Mostlinkedtemplates",
            "Mostrevisions",
            "OrphanedTimedText",
            "Shortpages",
            "Uncategorizedcategories",
            "Uncategorizedimages",
            "Uncategorizedpages",
            "Uncategorizedtemplates",
            "UnconnectedPages",
            "Unusedcategories",
            "Unusedimages",
            "Unusedtemplates",
            "Unwatchedpages",
            "Wantedcategories",
            "Wantedfiles",
            "Wantedpages",
            "Wantedtemplates",
            "Withoutinterwiki",
        ]
        # ---
        if qppage not in qppage_values:
            logger.info(f"<<lightred>> qppage {qppage} not in qppage_values.")

        def _load_data(body):
            query = body.get("query", {})
            return query.get("querypage") or query.get("results") or []

        results = self.login_bot.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
            max=max,
        )
        # ---
        logger.debug(f" len(results) = {len(results)}")
        # ---
        return results

    def get_template_pages(
        self,
        title: str,
        namespace: str = "*",
        max: int = 10000,
    ) -> list[Any]:
        # ---
        logger.debug(f'get_template_pages for template:"{title}", limit:"{max}",namespace:"{namespace}"')
        # ---
        params: dict[str, Any] = {
            "action": "query",
            # "prop": "info",
            "titles": title,
            "generator": "transcludedin",
            "gtinamespace": namespace,
            "gtilimit": "max",
            "formatversion": "2",
        }

        # ---
        def _load_data(body):
            return body.get("query", {}).get("pages") or []

        # ---
        results = self.login_bot.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
        )
        # ---
        # { "pageid": 2973452, "ns": 100, "title": "بوابة:سباق الدراجات الهوائية" }
        pages = [x["title"] for x in results]
        # ---
        logger.info(f"mdwiki_api.py : find {len(pages)} pages.")
        # ---
        return pages

    def get_image_url(self, title: str) -> str:
        # ---
        if not title.startswith("File:") and not title.startswith("ملف:"):
            title = f"File:{title}"
        # ---
        logger.debug(f' for file:"{title}":')
        # ---
        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "prop": "imageinfo",
            "titles": title,
            "iiprop": "url",
            "formatversion": "2",
        }
        # ---
        results = self.login_bot.client_request_safe(params, method="post")
        # ---
        if not results:
            return ""
        # ---
        data = results.get("query", {}).get("pages", [])
        # ---
        if data:
            data = data[0]
        # ---
        url = data.get("imageinfo", [{}])[0].get("url", "")
        # ---
        logger.info(f": image url: {url}")
        # ---
        return url

    def get_imageinfo(self, title: str) -> Any:
        # ---
        if not title.startswith("File:") and not title.startswith("ملف:"):
            title = f"File:{title}"
        # ---
        logger.debug(f' for file:"{title}":')
        # ---
        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "prop": "imageinfo",
            "titles": title,
            "iiprop": "url|userid|extmetadata|dimensions|commonmetadata|comment|bitdepth|badfile|archivename|canonicaltitle|mediatype|metadata|thumbmime|size|sha1|parsedcomment|mime|uploadwarning",
            "formatversion": "2",
        }
        # ---
        results = self.login_bot.client_request_safe(params, method="post")
        # ---
        if not results:
            return ""
        # ---
        data = results.get("query", {}).get("pages", [{}])[0]
        # ---
        return data

    def pageswithprop(
        self,
        pwppropname: str = "unlinkedwikibase_id",
        pwplimit=None,
        max=None,
    ) -> list[Any]:
        # ---
        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "list": "pageswithprop",
            "utf8": 1,
            "formatversion": "2",
            "pwplimit": "max",
            "pwppropname": "unlinkedwikibase_id",
            "pwpprop": "title|value",
        }
        # ---
        if pwplimit and str(pwplimit).isdigit():
            params["pwplimit"] = pwplimit
        # ---
        if pwppropname != "":
            params["pwppropname"] = pwppropname

        # ---
        def _load_data(body):
            return body.get("query", {}).get("pageswithprop") or []

        # ---
        results = self.login_bot.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
            max=max,
        )
        # ---
        logger.debug(f" len(results) = {len(results)}")
        # ---
        return results

    def get_titles_redirects(self, titles: list[str]) -> dict[str, str]:
        # ---
        redirects = {}
        # ---
        # for i in range(0, len(titles), 50): group = titles[i : i + 50]
        for title_chunk in self.chunk_titles(titles, chunk_size=50):
            params: dict[str, Any] = {
                "action": "query",
                "format": "json",
                "titles": "|".join(title_chunk),
                "redirects": 1,
                # "prop": "templates|langlinks",
                "utf8": 1,
                # "normalize": 1,
            }

            # ---
            def _load_data(body):
                return body.get("query", {}).get("redirects") or []

            # ---
            json1 = self.login_bot.post_continue_list(
                params=params,
                action="query",
                _load_data=_load_data,
            )
            # ---
            lists = {x["from"]: x["to"] for x in json1}
            # ---
            if lists:
                redirects.update(lists)
        # ---
        return redirects

    def expandtemplates(self, text: str) -> str:
        # ---
        params: dict[str, Any] = {
            "action": "expandtemplates",
            "format": "json",
            "text": text,
            "prop": "wikitext",
            "formatversion": 2,
        }
        # ---
        data = self.login_bot.client_request_safe(params)
        # ---
        if not data:
            return text
        # ---
        newtext = data.get("expandtemplates", {}).get("wikitext") or text
        # ---
        return newtext

    def parse_text(self, line, title: str) -> str:
        # ---
        params: dict[str, Any] = {
            "action": "parse",
            "prop": "wikitext",
            "text": line,
            "title": title,
            "pst": 1,
            "contentmodel": "wikitext",
            "utf8": 1,
            "formatversion": 2,
        }
        # ---
        # {"parse": {"title": "كريس فروم", "pageid": 2639244, "wikitext": "{{subst:user:Mr._Ibrahem/line2|Q76|P31}}", "psttext": "\"Q76\":{\n\"P31\":\"إنسان\"\n\n\n\n\n},"}}
        # ---
        data = self.login_bot.client_request_safe(params)
        # ---
        if not data:
            return ""
        # ---
        textnew = data.get("parse", {}).get("psttext", "")
        # ---
        textnew = textnew.replace("\\n\\n", "")
        # ---
        return textnew

    def upload_by_file(
        self,
        file_name,
        text: str,
        file_path,
        comment: str = "",
        ignorewarnings: bool = False,
    ) -> dict[str, Any]:
        # ---
        logger.info(f"<<lightyellow>> def . {file_name=}")
        # ---
        if file_name.startswith("File:"):
            file_name = file_name.replace("File:", "")
        # ---
        if file_name.startswith("ملف:"):
            file_name = file_name.replace("ملف:", "")
        # ---
        logger.info(f"<<lightyellow>> {file_path=}...")
        # ---
        params: dict[str, Any] = {
            "action": "upload",
            "format": "json",
            "filename": file_name,
            "comment": comment,
            "text": text,
            "utf8": 1,
        }
        # ---
        if ignorewarnings:
            params["ignorewarnings"] = 1
        # ---
        data = self.login_bot.client_request_safe(params, files={"file": open(file_path, "rb")})
        # ---
        upload_result = data.get("upload", {})
        # ---
        success = upload_result.get("result") == "Success"
        _error = data.get("error", {})
        # ---
        duplicate = upload_result.get("warnings", {}).get("duplicate", [""])[0].replace("_", " ")
        # ---
        if success:
            logger.info(f"<<lightgreen>> ** upload true .. [[File:{file_name}]] ")
            return {"success": True, **upload_result}
        # ---
        if duplicate:
            logger.info(f"<<lightred>> ** duplicate file: {duplicate}.")
        # ---
        return {"success": False, **upload_result}

    def _get_title_redirect_normalize(
        self,
        title: str,
        redirects: list[dict[str, dict]],
        normalized: list[dict[str, dict]],
    ) -> dict[str, Any]:
        # ---
        tab: dict[str, Any] = {
            "user_input": title,
            "redirect_to": "",
            "normalized_to": "",
            "real_title": title,
        }
        # ---
        normalized_tab = {x["to"]: x["from"] for x in normalized}
        # ---
        redirects_tab = {x["to"]: x["from"] for x in redirects}
        # ---
        if tab["user_input"] in redirects_tab:
            tab["redirect_to"] = tab["user_input"]
            tab["user_input"] = redirects_tab[tab["user_input"]]
        # ---
        if tab["user_input"] in normalized_tab:
            tab["normalized_to"] = tab["user_input"]
            tab["user_input"] = normalized_tab[tab["user_input"]]
        # ---
        if tab["user_input"] == title:
            return {}
        # ---
        return tab

    def get_page_info_from_wikipedia(
        self,
        title,
        findtemp: str = "",
    ) -> dict[str, Any]:
        title = title.strip()

        params: dict[str, Any] = {
            "action": "query",
            "titles": title,
            "redirects": 1,
            "prop": "langlinks|pageprops|templates|linkshere|flagged|categories",
            "ppprop": "wikibase_item",
            "tlnamespace": "10",
            "tllimit": "max",
        }
        if findtemp:
            params["tltemplates"] = findtemp

        tata = {
            "isRedirectPage": False,
            "exists": True,
            "from": "",
            "to": "",
            "title": "",
            "ns": "",
            "pageid": "",
            "countlinkshere": 0,
            "linkshere": {},
            "langlinks": {},
            "templates": {},
            "wikibase_item": "",
            "q": "",
        }
        table = {}

        json1 = self.login_bot.client_request_safe(params, method="get")

        if not json1:
            return {}

        title2 = title

        # {'batchcomplete': '', 'query': {'pages': {'361534': {'pageid': 361534, 'ns': 4, 'title': 'ويكيبيديا:ملعب'}}}}
        query = json1.get("query", {})

        if not query:
            return {}

        for xio in query.get("normalized", []):
            if xio["from"] == title:
                title2 = xio["to"]

        for red in query.get("redirects", []):
            logger.debug(f'page is redirects to : "{red["to"]}"')

            table2 = dict(tata)
            table2["isRedirectPage"] = True
            table2["exists"] = False
            table2["from"] = red["from"]
            table2["to"] = red["to"]
            table2["title"] = red["from"]
            table[red["from"]] = table2

        pages = query.get("pages", {})

        numb = 1

        for id2, kk in pages.items():
            _title = kk.get("title", "")
            table[_title] = dict(tata)
            table[_title]["title"] = _title

            if id2 == "-1":
                logger.debug(f'a {numb}/{len(pages)} title:{_title}, id :"{id2}"')
                table[_title]["exists"] = False
                continue

            table[_title]["ns"] = kk.get("ns", "")
            if "missing" in kk:
                table[_title]["exists"] = False

            table[_title]["langlinks"] = {x["lang"]: x["*"] for x in kk.get("langlinks", [])}

            table[_title]["flagged"] = kk.get("flagged", False) is not False

            table[_title]["pageid"] = kk.get("pageid", "")

            q_q = kk.get("pageprops", {}).get("wikibase_item", "")
            table[_title]["wikibase_item"] = q_q
            table[_title]["q"] = q_q
            linkshere = {x["title"]: x for x in kk.get("linkshere", []) if x["ns"] in [0, 10]}
            table[_title]["linkshere"] = linkshere
            table[_title]["countlinkshere"] = len(linkshere.keys())

            table[_title]["categories"] = [x["title"] for x in kk.get("categories", [])]

            table[_title]["templates"] = [x["title"] for x in kk.get("templates", [])]

            table[_title]["iwlinks"] = {x["prefix"]: x["*"] for x in kk.get("iwlinks", [])}

        result = table

        if title in table:
            result = table[title]
        elif title2 in table:
            result = table[title2]

        return result

    def post_params(
        self,
        params,
        method: str = "get",
        files=None,
        **kwargs,
    ) -> dict[str, Any]:
        # ---
        return self.login_bot.client_request_safe(
            params,
            method=method,
            files=files,
            **kwargs,
        )

    def client_request_safe(
        self,
        params,
        method: str = "get",
        files=None,
        **kwargs,
    ) -> dict[str, Any]:
        # ---
        return self.login_bot.client_request_safe(
            params,
            method=method,
            files=files,
            **kwargs,
        )

    def users_infos(self, ususers: list[str]):
        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "list": "users",
            "formatversion": "2",
            "usprop": "groups",
            "ususers": ususers,
        }

        data = self.login_bot.client_request_safe(params, method="get")

        data = data.get("query", {}).get("users", [{}])

        return data

    def __repr__(self) -> str:
        return f"NewApi(lang={self.lang!r}, username={self.username!r})"


__all__ = [
    "NewApi",
]
