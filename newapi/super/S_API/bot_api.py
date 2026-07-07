""" """

import copy
import datetime
import logging
from collections.abc import KeysView
from datetime import timedelta
from typing import Any, Callable

import tqdm

from ...api_client import WikiLoginClient
from ...client_wiki.api_utils.ask_bot import AskBot
from ...client_wiki.api_utils.handel_errors import HandleErrors
from ...client_wiki.api_utils.lang_codes import change_codes

logger = logging.getLogger(__name__)


class NewApiHelpers:
    def __init__(self):
        pass

    def chunk_titles(self, titles, chunk_size: int = 50, noprint: bool = False):
        # ---
        if isinstance(titles, dict):
            titles = list(titles.keys())

        elif isinstance(titles, KeysView):
            # TypeError: 'dict_keys' object is not subscriptable
            titles = list(titles)
        # ---
        result = [titles[i : i + chunk_size] for i in range(0, len(titles), chunk_size)]
        # ---
        if not noprint:
            result = tqdm.tqdm(result, desc=f"chunk_titles {len(titles)} split to {len(result)} chunks")
        # ---
        return result

class NewApi(AskBot, NewApiHelpers):
    def __init__(self, login_bot: WikiLoginClient, lang: str = "", family: str = "wikipedia") -> None:
        # ---
        self.error_handler = HandleErrors()
        self.login_bot = login_bot
        # ---
        self.username = getattr(self, "username", "")
        self.lang = change_codes.get(lang) or lang
        # ---
        super().__init__()

    def get_username(self):
        return self.username

    def Find_pages_exists_or_not(
        self,
        liste,
        get_redirect: bool = False,
        noprint: bool = False,
        chunk_size: int = 50,
    ):
        # ---
        done = 0
        # ---
        pages_table = []
        normalized_table = []
        # ---
        # ---
        for titles in self.chunk_titles(liste, chunk_size=chunk_size, noprint=noprint):
            # ---
            done += len(titles)
            # ---
            params = {
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
        if not noprint:
            logger.info(f"Find_pages_exists_or_not : missing:{missing}, exists: {exists}, redirects: {redirects}")
        # ---
        return table

    def Find_pages_exists_or_not_with_qids(
        self,
        liste,
        get_redirect: bool = False,
        noprint: bool = False,
        return_all_jsons: bool = False,
        use_user_input_title: bool = False,
        chunk_size: int = 50,
    ):
        # ---
        done = 0
        # ---
        pages_table = []
        normalized_table = []
        redirects_table = []
        # ---
        all_jsons = {}
        # ---
        for titles in self.chunk_titles(liste, chunk_size=chunk_size, noprint=noprint):
            # ---
            done += len(titles)
            # ---
            params = {
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
            title_tab = self.get_title_redirect_normalize(title_x, redirects_table, normalized_table)
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
        if not noprint:
            logger.info(f"Find_pages_exists_or_not : missing:{missing}, exists: {exists}, redirects: {redirects}")
        # ---
        if return_all_jsons:
            return table, all_jsons
        # ---
        return table

    def Get_All_pages(
        self,
        start: str = "",
        namespace: str = "0",
        limit: int = "max",
        apfilterredir: str = "",
        ppprop: str = "",
        limit_all: int = 100000,
    ) -> list[str]:
        # ---
        logger.debug(
            f"Get_All_pages for start:{start}, limit:{limit},namespace:{namespace},apfilterredir:{apfilterredir}"
        )
        # ---
        params = {
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
            del params["apnamespace"]
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

        # ---
        newp = self.post_continue_list(params=params, action="query", max=limit_all, _load_data=_load_data)
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

    def Get_All_pages_generator(
        self,
        start: str = "",
        namespace: str = "0",
        limit: int = "max",
        filterredir: str = "",
        ppprop: str = "",
        limit_all: int = 100000,
    ):
        # ---
        logger.debug(
            f"Get_All_pages_generator for start:{start}, limit:{limit},namespace:{namespace},filterredir:{filterredir}"
        )
        # ---
        params = {
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
        newp = self.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
            max=limit_all,
        )
        # ---
        logger.debug(f"<<lightpurple>> --- Get_All_pages_generator : find {len(newp)} pages.")
        # ---
        Main_table = {x["title"]: x for x in newp}
        # ---
        logger.debug(f"len of Main_table {len(Main_table)}.")
        # ---
        logger.info(f"bot_api.py Get_All_pages_generator : find {len(Main_table)} pages.")
        # ---
        return Main_table

    def PrefixSearch(self, pssearch: str = "", ns: str = "0", pslimit: str = "max", limit_all: int = 100000):
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
        params = {
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
        if ns.isdigit():
            params["psnamespace"] = ns
        # ---
        if pslimit.isdigit():
            params["pslimit"] = pslimit

        # ---
        def _load_data(body):
            return body.get("query", {}).get("prefixsearch") or []

        # ---
        newp = self.post_continue_list(
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

    def Search(
        self,
        value: str = "",
        ns: str = "*",
        offset: int = "",
        srlimit: str = "max",
        return_dict: bool = False,
        addparams=None,
    ):
        # ---
        logger.debug(f'bot_api. for "{value}",ns:{ns}')
        # ---
        if not srlimit:
            srlimit = "max"
        # ---
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": value,
            "srnamespace": 0,
            "srlimit": srlimit,
            "formatversion": 1,
        }
        # ---
        if ns:
            params["srnamespace"] = ns
        # ---
        if offset:
            params["sroffset"] = offset
        # ---
        if addparams:
            addparams = {x: v for x, v in addparams.items() if v and x not in params}
            params = {**params, **addparams}

        # ---
        def _load_data(body):
            return body.get("query", {}).get("search") or []

        # ---
        search = self.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
        )
        # ---
        results = []
        # ---
        for pag in search:
            if return_dict:
                results.append(pag)
            else:
                results.append(pag["title"])
        # ---
        logger.debug(f'bot_api. find "{len(search)}" all result: {len(results)}')
        # ---
        return results

    def Get_Newpages(
        self,
        limit: int = 5000,
        namespace: str = "0",
        rcstart: str = "",
        user: str = "",
        three_houers: bool = False,
        offset_minutes: bool = False,
        offset_hours: bool = False,
    ):
        if three_houers:
            dd = datetime.datetime.now(datetime.UTC) - timedelta(hours=3)
            rcstart = dd.strftime("%Y-%m-%dT%H:%M:00.000Z")

        elif offset_minutes and isinstance(offset_minutes, int):
            dd = datetime.datetime.now(datetime.UTC) - timedelta(minutes=offset_minutes)
            rcstart = dd.strftime("%Y-%m-%dT%H:%M:00.000Z")

        params = {
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
        json1 = self.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
            max=limit,
        )
        Main_table = [x["title"] for x in json1]

        logger.debug(f'bot_api. find "{len(Main_table)}" result. s')

        return Main_table

    def UserContribs(self, user, limit: int = 5000, namespace: str = "*", ucshow: str = ""):
        # ---
        params = {
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
        results = self.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
            max=limit,
        )
        # ---
        results = [x["title"] for x in results]
        # ---
        return results

    def Get_langlinks_for_list(self, titles, targtsitecode: str = "", numbes: int = 40):
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
        logger.debug(f'bot_api.Get_langlinks_for_list for "{len(titles)} pages". in wiki:{self.lang}')
        # ---
        targtsitecode = targtsitecode.removesuffix("wiki")
        # ---
        #  error: {'code': 'toomanyvalues', 'info': 'Too many values supplied for parameter "titles". The limit is 50.', 'parameter': 'titles', 'limit': 50, 'lowlimit': 50, 'highlimit': 500, '*': ''}
        # if self.lang != "ar":
        # ---
        numbes = 50
        # ---
        params = {
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
            f'bot_api.Get_langlinks_for_list find "{len(table)}" in table,find_targtsitecode:{targtsitecode}:{find_targtsitecode}'
        )
        # ---
        return table

    def get_logs(self, title):
        # ---
        params = {
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

    def get_extlinks(self, title):
        params = {
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
        results = self.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
        )
        # ---
        links = [x["url"] for x in results]
        # ---
        return sorted(set(links))

    def get_pageassessments(self, titles):
        if isinstance(titles, list):
            titles = "|".join(titles)
        # ---
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageassessments",
            "titles": titles,
            "utf8": 1,
            "ellimit": "max",
            "formatversion": 2,
        }

        # ---
        def _load_data(body):
            return body.get("query", {}).get("pages") or []

        # ---
        results = self.post_continue_list(
            params,
            "query",
            "pages",
        )
        # ---
        return results

    def get_revisions(self, title, rvprop: str = "comment|timestamp|user|content|ids", options=None):
        # ---
        params = {
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
        results = self.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
        )
        # ---
        return results

    def querypage_list(self, qppage: str = "Wantedcategories", qplimit=None, max=None):
        # ---
        params = {
            "action": "query",
            "format": "json",
            "list": "querypage",
            # "qppage": "Wantedcategories",
            "qplimit": "max",
            "formatversion": 2,
        }
        # ---
        if qplimit and qplimit.isdigit():
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

        # ---
        def _load_data(body):
            return body.get("query", {}).get("querypage") or []

        # ---
        results = self.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
            max=max,
        )
        # ---
        logger.debug(f" len(results) = {len(results)}")
        # ---
        return results

    def Get_template_pages(self, title, namespace: str = "*", max: int = 10000):
        # ---
        logger.debug(f'Get_template_pages for template:"{title}", limit:"{max}",namespace:"{namespace}"')
        # ---
        params = {
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
        results = self.post_continue_list(
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

    def Get_image_url(self, title):
        # ---
        if not title.startswith("File:") and not title.startswith("ملف:"):
            title = f"File:{title}"
        # ---
        logger.debug(f' for file:"{title}":')
        # ---
        params = {
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

    def Get_imageinfo(self, title):
        # ---
        if not title.startswith("File:") and not title.startswith("ملف:"):
            title = f"File:{title}"
        # ---
        logger.debug(f' for file:"{title}":')
        # ---
        params = {
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

    def pageswithprop(self, pwppropname: str = "unlinkedwikibase_id", pwplimit=None, max=None):
        # ---
        params = {
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
        if pwplimit and pwplimit.isdigit():
            params["pwplimit"] = pwplimit
        # ---
        if pwppropname != "":
            params["pwppropname"] = pwppropname

        # ---
        def _load_data(body):
            return body.get("query", {}).get("pageswithprop") or []

        # ---
        results = self.post_continue_list(
            params=params,
            action="query",
            _load_data=_load_data,
            max=max,
        )
        # ---
        logger.debug(f" len(results) = {len(results)}")
        # ---
        return results

    def get_titles_redirects(self, titles):
        # ---
        redirects = {}
        # ---
        # for i in range(0, len(titles), 50): group = titles[i : i + 50]
        for title_chunk in self.chunk_titles(titles, chunk_size=50):
            params = {
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
            json1 = self.post_continue_list(
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

    def Add_To_Bottom(self, text: str, summary, title, poss: str = "Head|Bottom"):
        # ---
        if not title.strip():
            logger.info('** .. title == ""')
            return False
        # ---
        if not text.strip():
            logger.info('** .. text == ""')
            return False
        # ---
        logger.debug(f"** .. [[{title}]] ")
        # ---
        user = self.username
        # ---
        ask = self.ask_put(
            newtext=text,
            message=f"** Add_To {poss} .. [[{title}]] ",
            job="Add_To_Bottom",
            username=user,
            summary=summary,
        )
        # ---
        if ask is False:
            return False
        # ---
        params = {
            "action": "edit",
            "format": "json",
            "title": title,
            "summary": summary,
            "notminor": 1,
            "nocreate": 1,
            "utf8": 1,
        }
        # ---
        if poss == "Head":
            params["prependtext"] = f"{text.strip()}\n"
        else:
            params["appendtext"] = f"\n{text.strip()}"
        # ---
        results = self.login_bot.client_request_safe(params)
        # ---
        if not results:
            return ""
        # ---
        data = results.get("edit", {})
        result = data.get("result", "")
        # ---
        if result == "Success":
            logger.info(f"<<lightgreen>>** True. title:({title})")
            return True
        # ---
        error = results.get("error", {})
        # ---
        if error != {}:
            print(results)
            er = self.error_handler.handle_err(error, function="Add_To_Bottom", params=params)
            # ---
            return er
        # ---
        return True

    def move(
        self,
        old_title,
        to,
        reason: str = "",
        noredirect: bool = False,
        movesubpages: bool = False,
        return_dict: bool = False,
    ):
        # ---
        logger.info(f"<<lightyellow>> def [[{old_title}]] to [[{to}]] ")
        # ---
        params = {
            "action": "move",
            "format": "json",
            "from": old_title,
            "to": to,
            "movetalk": 1,
            "formatversion": 2,
        }
        # ---
        if noredirect:
            params["noredirect"] = 1
        if movesubpages:
            params["movesubpages"] = 1
        # ---
        if reason:
            params["reason"] = reason
        # ---
        if old_title == to:
            logger.debug(f"<<lightred>>** old_title == to {to} ")
            return {}
        # ---
        message = f"Do you want to move page:[[{old_title}]] to [[{to}]]?"
        # ---
        user = self.username
        # ---
        if not self.ask_put(message=message, job="move", username=user):
            return {}
        # ---
        data = self.login_bot.client_request_safe(params)
        # { "move": { "from": "d", "to": "d2", "reason": "wrong", "redirectcreated": true, "moveoverredirect": false } }
        # ---
        if not data:
            logger.info("no data")
            return {}
        # ---
        _expend_data = {
            "move": {
                "from": "User:Mr. Ibrahem",
                "to": "User:Mr. Ibrahem/x",
                "reason": "wrong title",
                "redirectcreated": True,
                "moveoverredirect": False,
                "talkmove-errors": [
                    {
                        "message": "content-not-allowed-here",
                        "params": [
                            "Structured Discussions board",
                            "User talk:Mr. Ibrahem/x",
                            "main",
                        ],
                        "code": "contentnotallowedhere",
                        "type": "error",
                    },
                    {
                        "message": "flow-error-allowcreation-flow-create-board",
                        "params": [],
                        "code": "flow-error-allowcreation-flow-create-board",
                        "type": "error",
                    },
                ],
                "subpages": {
                    "errors": [
                        {
                            "message": "cant-move-subpages",
                            "params": [],
                            "code": "cant-move-subpages",
                            "type": "error",
                        }
                    ]
                },
                "subpages-talk": {
                    "errors": [
                        {
                            "message": "cant-move-subpages",
                            "params": [],
                            "code": "cant-move-subpages",
                            "type": "error",
                        }
                    ]
                },
            }
        }
        # ---
        move_done = data.get("move", {})
        error = data.get("error", {})
        error_code = error.get("code", "")  # missingtitle
        # ---
        # elif "Please choose another name." in r4:
        # ---
        if move_done:
            logger.info("<<lightgreen>>** true.")
            # ---
            if return_dict:
                return move_done
            # ---
            return True
        # ---
        if error:
            if error_code == "ratelimited":
                logger.info("<<red>> ratelimited:")
                return self.move(
                    old_title,
                    to,
                    reason=reason,
                    noredirect=noredirect,
                    movesubpages=movesubpages,
                    return_dict=return_dict,
                )

            if error_code == "articleexists":
                logger.info("<<red>> articleexists")
                return "articleexists"

            logger.info("<<red>> error")
            logger.info(error)

            return {}
        # ---
        return {}

    def expandtemplates(self, text: str):
        # ---
        params = {
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

    def Parse_Text(self, line, title):
        # ---
        params = {
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

    def upload_by_file(self, file_name, text: str, file_path, comment: str = "", ignorewarnings: bool = False):
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
        params = {
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
            return True
        # ---
        if duplicate:
            logger.info(f"<<lightred>> ** duplicate file: {duplicate}.")
        # ---
        return data

    def get_title_redirect_normalize(self, title, redirects, normalized):
        # ---
        redirects = redirects or []
        normalized = normalized or []
        # ---
        tab = {
            "user_input": title,
            "redirect_to": "",
            "normalized_to": "",
            "real_title": title,
        }
        # ---
        normalized = {x["to"]: x["from"] for x in normalized}
        # ---
        redirects = {x["to"]: x["from"] for x in redirects}
        # ---
        if tab["user_input"] in redirects:
            tab["redirect_to"] = tab["user_input"]
            tab["user_input"] = redirects[tab["user_input"]]
        # ---
        if tab["user_input"] in normalized:
            tab["normalized_to"] = tab["user_input"]
            tab["user_input"] = normalized[tab["user_input"]]
        # ---
        if tab["user_input"] == title:
            return {}
        # ---
        return tab

    def post_params(
        self,
        params,
        method: str = "get",
        files=None,
        **kwargs,
    ):
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
    ):
        # ---
        return self.login_bot.client_request_safe(
            params,
            method=method,
            files=files,
            **kwargs,
        )

    def post_continue_list(
        self,
        params: dict,
        action: str,
        _load_data: Callable,
        max: int | None = None,
    ) -> dict[str, Any]:
        """
        Drive a MediaWiki API continuation query to completion.

        Iterates the ``continue`` token until all pages are fetched or *max*
        results have been collected.

        Args:
            params:     Base API parameters.
            action:     Top-level JSON key to extract results from
                        (e.g. ``"query"``).
            max:        Stop accumulating after this many results.

        Returns:
            Accumulated results as a list
        """
        logger.debug("action=%s", action)

        if isinstance(max, str) and max.isdigit():
            max = int(max)
        if max == 0:
            max = 500_000
        if max is None:
            max = 500_000
        results = []
        continue_params: dict = {}

        while True:
            page_params = copy.deepcopy(params)

            if not continue_params:
                break
            logger.debug("Applying continue_params: %s", continue_params)
            page_params.update(continue_params)

            body = self.login_bot.client_request(page_params)

            if not body:
                logger.debug("empty response, stopping")
                break

            continue_params = body.get("continue", {})

            data = _load_data(body)

            if not data:
                logger.debug("no data in response, stopping")
                break

            logger.debug("+%d items (total %d)", len(data), len(results))

            if len(results) >= max:
                logger.debug("max=%d reached, stopping", max)
                break

            results.extend(data)

        logger.debug("done, %d total results", len(results))
        return results
