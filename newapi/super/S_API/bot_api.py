"""
from newapi.page import NEW_API
# api_new  = NEW_API('ar', family='wikipedia')
# login    = api_new.Login_to_wiki()
# cxtoken  = api_new.get_cxtoken()
# move_it  = api_new.move(old_title, to, reason="", noredirect=False, movesubpages=False)
# upload   = api_new.upload_by_file(file_name, text, file_path, comment="")
# pages    = api_new.Find_pages_exists_or_not(liste, get_redirect=False)
# json1    = api_new.post_params(params, addtoken=False)
# pages    = api_new.Get_All_pages(start='', namespace="0", limit="max", apfilterredir='', limit_all=0)
# pages    = api_new.PrefixSearch(pssearch="", ns="0", pslimit="max", limit_all=100000)
# all_pages= api_new.Get_All_pages_generator(start="", namespace="0", limit="max", filterredir="", ppprop="", limit_all=100000)
# search   = api_new.Search(value='', ns="", offset='', srlimit="max", RETURN_dict=False, addparams={})
# newpages = api_new.Get_Newpages(limit="max", namespace="0", rcstart="", user='')
# usercont = api_new.UserContribs(user, limit=5000, namespace="*", ucshow="")
# l_links  = api_new.Get_langlinks_for_list(titles, targtsitecode="", numbes=50)
# text_w   = api_new.expandtemplates(text)
# subst    = api_new.Parse_Text('{{subst:page_name}}', title)
# extlinks = api_new.get_extlinks(title)
# revisions= api_new.get_revisions(title)
# logs     = api_new.get_logs(title)
# wantedcategories  = api_new.querypage_list(qppage='Wantedcategories|Wantedfiles', qplimit="max", Max=5000)
# pages  = api_new.Get_template_pages(title, namespace="*", Max=10000)
# pages_props  = api_new.pageswithprop(pwppropname="unlinkedwikibase_id", Max=None)
# img_url  = api_new.Get_image_url(title)
# img_info = api_new.Get_imageinfo(title)
# added    = api_new.Add_To_Bottom(text, summary, title, poss="Head|Bottom")
# titles   = api_new.get_titles_redirects(titles)
# titles   = api_new.get_pageassessments(titles)
# users    = api_new.users_infos(ususers=["Mr. Ibrahem"])
Usage:
from newapi.page import NEW_API
# ---
login_done_lang = {1:''}
# ---
# في بعض البوتات التي يتم ادخال اللغة من خلال وظائف معينة
# ---
if login_done_lang[1] != code:
    login_done_lang[1] = code
    api_new = NEW_API(code, family='wikipedia')
    api_new.Login_to_wiki()
"""

import datetime
import logging
import sys
import time
from collections.abc import KeysView
from datetime import timedelta

# ---
import tqdm

logger = logging.getLogger(__name__)
from ...api_utils.lang_codes import change_codes
from .bot import BOTS_APIS


class NEW_API(BOTS_APIS):
    def __init__(self, login_bot, lang="", family="wikipedia"):
        # ---
        self.login_bot = login_bot
        # ---
        self.user_login = login_bot.user_login
        # ---
        self.username = getattr(self, "username", "")
        # self.family = family
        self.lang = change_codes.get(lang) or lang
        # ---
        # self.family = family
        # self.endpoint = f"https://{lang}.{family}.org/w/api.php"
        # ---
        self.cxtoken_expiration = 0
        self.cxtoken = ""
        # ---
        super().__init__()

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

    def post_continue(
        self,
        params,
        action,
        _p_="pages",
        p_empty=None,
        Max=500000,
        first=False,
        _p_2="",
        _p_2_empty=None,
    ):
        return self.login_bot.post_continue(
            params,
            action,
            _p_=_p_,
            p_empty=p_empty,
            Max=Max,
            first=first,
            _p_2=_p_2,
            _p_2_empty=_p_2_empty,
        )

    def get_username(self):
        return self.username

    def Login_to_wiki(self):
        # ---
        # self.log_to_wiki_1()
        return

    def Find_pages_exists_or_not(self, liste, get_redirect=False, noprint=False):
        # ---
        done = 0
        # ---
        all_jsons = {}
        # ---
        for titles in self.chunk_titles(liste, chunk_size=50, noprint=noprint):
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
            # if get_redirect: params["redirects"] = 1
            # ---
            json1 = self.post_params(params)
            # ---
            if not json1:
                if not noprint:
                    logger.info("<<lightred>> error when Find_pages_exists_or_not")
                # return table
                continue
            # ---
            all_jsons = self.merge_all_jsons_deep(all_jsons, json1)
        # ---
        redirects = 0
        missing = 0
        exists = 0
        # ---
        query_table = all_jsons.get("query", {})
        # ---
        normalz = query_table.get("normalized", [])
        normalized = {red["to"]: red["from"] for red in normalz}
        # ---
        query_pages = query_table.get("pages", [])
        # ---
        table = {}
        # ---
        for kk in query_pages:
            # ---
            if isinstance(query_pages, dict):
                kk = query_pages[kk]
            # ---
            tit = kk.get("title", "")
            # ---
            if not tit:
                continue
            # ---
            tit = normalized.get(tit, tit)
            # ---
            table[tit] = True
            # ---
            if "missing" in kk:
                table[tit] = False
                missing += 1
            elif "redirect" in kk and get_redirect:
                table[tit] = "redirect"
                redirects += 1
            else:
                exists += 1
        # ---
        if not noprint:
            logger.info(
                f"Find_pages_exists_or_not : missing:{missing}, exists: {exists}, redirects: {redirects}"
            )
        # ---
        return table

    def Find_pages_exists_or_not_with_qids(
        self,
        liste,
        get_redirect=False,
        noprint=False,
        return_all_jsons=False,
        use_user_input_title=False,
        chunk_size=50,
    ):
        # ---
        done = 0
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
            json1 = self.post_params(params)
            # ---
            if not json1:
                if not noprint:
                    logger.info("<<lightred>> error when Find_pages_exists_or_not")
                # return table
                continue
            # ---
            all_jsons = self.merge_all_jsons_deep(all_jsons, json1)
        # ---
        redirects = 0
        missing = 0
        exists = 0
        # ---
        query_table = all_jsons.get("query", {})
        # ---
        normalized_table = query_table.get("normalized", [])
        redirects_table = query_table.get("redirects", [])
        # ---
        query_pages = query_table.get("pages", [])
        # ---
        table = {}
        # ---
        for kk in query_pages:
            # ---
            if isinstance(query_pages, dict):
                kk = query_pages[kk]
            # ---
            # {'pageid': 3191861, 'ns': 0, 'title': 'Abdomen', 'contentmodel': 'wikitext', 'pagelanguage': 'en', 'pagelanguagehtmlcode': 'en', 'pagelanguagedir': 'ltr', 'touched': '2025-07-31T20:53:20Z', 'lastrevid': 1302382633, 'length': 25596, 'pageprops': {'wikibase_item': 'Q9597'}}
            # ---
            wikibase_item = kk.get("pageprops", {}).get("wikibase_item", "")
            # ---
            title_x = kk.get("title", "")
            # ---
            if not title_x:
                continue
            # ---
            # { "user_input": title, "redirect_to": "", "normalized_to": "", "real_title": title, }
            title_tab = self.get_title_redirect_normalize(
                title_x, redirects_table, normalized_table
            )
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
            logger.info(
                f"Find_pages_exists_or_not : missing:{missing}, exists: {exists}, redirects: {redirects}"
            )
        # ---
        if return_all_jsons:
            return table, all_jsons
        # ---
        return table

    def Get_All_pages(
        self,
        start="",
        namespace="0",
        limit="max",
        apfilterredir="",
        ppprop="",
        limit_all=100000,
    ):
        # ---
        logger.test_print(
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
        newp = self.post_continue(
            params, "query", _p_="allpages", p_empty=[], Max=limit_all
        )
        # ---
        logger.test_print(
            f"<<lightpurple>> --- Get_All_pages : find {len(newp)} pages."
        )
        # ---
        Main_table = [x["title"] for x in newp]
        # ---
        logger.test_print(f"len of Main_table {len(Main_table)}.")
        # ---
        logger.info(f"bot_api.py Get_All_pages : find {len(Main_table)} pages.")
        # ---
        return Main_table

    def PrefixSearch(self, pssearch="", ns="0", pslimit="max", limit_all=100000):
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
        logger.test_print(
            f"PrefixSearch for start:{pssearch}, pslimit:{pslimit}, ns:{ns}"
        )
        # ---
        pssearch = pssearch.strip() if pssearch else ""
        # ---
        if not pssearch:
            return
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
        newp = self.post_continue(
            params, "query", _p_="prefixsearch", p_empty=[], Max=limit_all
        )
        # ---
        logger.test_print(f"<<lightpurple>> --- PrefixSearch : find {len(newp)} pages.")
        # ---
        Main_table = [x["title"] for x in newp]
        # ---
        logger.test_print(f"len of Main_table {len(Main_table)}.")
        # ---
        logger.info(f"bot_api.py PrefixSearch : find {len(Main_table)} pages.")
        # ---
        return Main_table

    def Get_All_pages_generator(
        self,
        start="",
        namespace="0",
        limit="max",
        filterredir="",
        ppprop="",
        limit_all=100000,
    ):
        # ---
        logger.test_print(
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
        newp = self.post_continue(
            params, "query", _p_="pages", p_empty=[], Max=limit_all
        )
        # ---
        logger.test_print(
            f"<<lightpurple>> --- Get_All_pages_generator : find {len(newp)} pages."
        )
        # ---
        Main_table = {x["title"]: x for x in newp}
        # ---
        logger.test_print(f"len of Main_table {len(Main_table)}.")
        # ---
        logger.info(
            f"bot_api.py Get_All_pages_generator : find {len(Main_table)} pages."
        )
        # ---
        return Main_table

    def Search(
        self,
        value="",
        ns="*",
        offset="",
        srlimit="max",
        RETURN_dict=False,
        addparams=None,
    ):
        # ---
        logger.test_print(f'bot_api.Search for "{value}",ns:{ns}')
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
        search = self.post_continue(params, "query", _p_="search", p_empty=[])
        # ---
        results = []
        # ---
        for pag in search:
            if RETURN_dict:
                results.append(pag)
            else:
                results.append(pag["title"])
        # ---
        logger.test_print(
            f'bot_api.Search find "{len(search)}" all result: {len(results)}'
        )
        # ---
        return results

    def Get_Newpages(
        self,
        limit=5000,
        namespace="0",
        rcstart="",
        user="",
        three_houers=False,
        offset_minutes=False,
        offset_hours=False,
    ):
        if three_houers:
            dd = datetime.datetime.utcnow() - timedelta(hours=3)
            rcstart = dd.strftime("%Y-%m-%dT%H:%M:00.000Z")

        elif offset_minutes and isinstance(offset_minutes, int):
            dd = datetime.datetime.utcnow() - timedelta(minutes=offset_minutes)
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

        json1 = self.post_continue(
            params, "query", _p_="recentchanges", p_empty=[], Max=limit
        )

        Main_table = [x["title"] for x in json1]

        logger.test_print(f'bot_api.Get_Newpages find "{len(Main_table)}" result. s')

        return Main_table

    def UserContribs(self, user, limit=5000, namespace="*", ucshow=""):
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
        results = self.post_continue(
            params, "query", _p_="usercontribs", p_empty=[], Max=limit
        )
        # ---
        results = [x["title"] for x in results]
        # ---
        return results

    def chunk_titles(self, titles, chunk_size=50, noprint=False):
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
            result = tqdm.tqdm(
                result, desc=f"chunk_titles {len(titles)} split to {len(result)} chunks"
            )
        # ---
        return result

    def Get_langlinks_for_list(self, titles, targtsitecode="", numbes=40):
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
        logger.test_print(
            f'bot_api.Get_langlinks_for_list for "{len(titles)} pages". in wiki:{self.lang}'
        )
        # ---
        if targtsitecode.endswith("wiki"):
            targtsitecode = targtsitecode[:-4]
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
            logger.test_print(f'params["lllang"] = {targtsitecode}')
        # ---
        find_targtsitecode = 0
        normalized = {}
        table = {}
        # ---
        for title_chunk in self.chunk_titles(titles, chunk_size=numbes):
            params["titles"] = "|".join(title_chunk)
            # ---
            # printe.test_print(f'bot_api.Get_langlinks_for_list work for {len(group)} pages')
            # ---
            json1 = self.post_params(params)
            # ---
            if not json1:
                logger.info("bot_api.Get_langlinks_for_list json1 is empty")
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
        data = self.post_params(params)
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
        results = self.post_continue(
            params, "query", "pages", [], first=True, _p_2="extlinks", _p_2_empty=[]
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
        results = self.post_continue(
            params,
            "query",
            "pages",
            [],
            first=False,
            _p_2="pageassessments",
            _p_2_empty=[],
        )
        # ---
        return results

    def get_revisions(
        self, title, rvprop="comment|timestamp|user|content|ids", options=None
    ):
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
        results = self.post_continue(params, "query", _p_="pages", p_empty=[])
        # ---
        return results

    def querypage_list(self, qppage="Wantedcategories", qplimit=None, Max=None):
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
        if qplimit.isdigit():
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
        results = self.post_continue(
            params, "query", _p_="querypage", p_empty=[], Max=Max
        )
        # ---
        logger.test_print(f"querypage_list len(results) = {len(results)}")
        # ---
        return results

    def Get_template_pages(self, title, namespace="*", Max=10000):
        # ---
        logger.test_print(
            f'Get_template_pages for template:"{title}", limit:"{Max}",namespace:"{namespace}"'
        )
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
        results = self.post_continue(params, "query", _p_="pages", p_empty=[])
        # ---
        # { "pageid": 2973452, "ns": 100, "title": "بوابة:سباق الدراجات الهوائية" }
        pages = [x["title"] for x in results]
        # ---
        logger.info(f"mdwiki_api.py Get_template_pages : find {len(pages)} pages.")
        # ---
        return pages

    def Get_image_url(self, title):
        # ---
        if not title.startswith("File:") and not title.startswith("ملف:"):
            title = f"File:{title}"
        # ---
        logger.test_print(f'Get_image_url for file:"{title}":')
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
        results = self.post_params(params)
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
        logger.info(f"Get_image_url: image url: {url}")
        # ---
        return url

    def Get_imageinfo(self, title):
        # ---
        if not title.startswith("File:") and not title.startswith("ملف:"):
            title = f"File:{title}"
        # ---
        logger.test_print(f'Get_imageinfo for file:"{title}":')
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
        results = self.post_params(params)
        # ---
        if not results:
            return ""
        # ---
        data = results.get("query", {}).get("pages", [{}])[0]
        # ---
        return data

    def pageswithprop(self, pwppropname="unlinkedwikibase_id", pwplimit=None, Max=None):
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
        results = self.post_continue(
            params, "query", _p_="pageswithprop", p_empty=[], Max=Max
        )
        # ---
        logger.test_print(f"pageswithprop len(results) = {len(results)}")
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
            json1 = self.post_continue(params, "query", _p_="redirects", p_empty=[])
            # ---
            lists = {x["from"]: x["to"] for x in json1}
            # ---
            if lists:
                redirects.update(lists)
        # ---
        return redirects

    def get_cxtoken(self):
        # ---
        if self.cxtoken and self.cxtoken_expiration:
            current_time = int(time.time())
            if current_time < self.cxtoken_expiration:
                return self.cxtoken
            else:
                self.cxtoken = ""
                self.cxtoken_expiration = 0
        # ---
        print("get_cxtoken")
        # ---
        params = {"action": "cxtoken", "format": "json"}
        # ---
        data = self.post_params(params, addtoken=True)
        # ---
        if not data:
            return ""
        # ---
        # { "jwt": "eyJ0eXAiOiJ.....", "exp": 1728172536, "age": 3600 }
        jwt = data.get("jwt", "")
        exp = data.get("exp", 0)
        # ---
        if jwt:
            self.cxtoken = jwt
            self.cxtoken_expiration = exp
        # ---
        return jwt

    def users_infos(self, ususers=[]):
        # ---
        params = {
            "action": "query",
            "format": "json",
            "list": "users",
            "utf8": 1,
            "formatversion": "2",
            "usprop": "groups|implicitgroups|editcount|gender|registration",
            "ususers": "Mr.Ibrahembot",
        }
        # ---
        all_usprops = [
            "groups",
            "implicitgroups",
            "cancreate",
            "editcount",
            "centralids",
            "blockinfo",
            "emailable",
            "gender",
            "groupmemberships",
            "registration",
            "rights",
        ]
        # ---
        ususers = list(set(ususers))
        # ---
        params["ususers"] = "|".join(ususers)
        # ---
        results = self.post_continue(params, "query", _p_="users", p_empty=[])
        # ---
        logger.test_print(f"users_infos len(results) = {len(results)}")
        # ---
        results = [dict(x) for x in results]
        # ---
        return results
