""" """

from __future__ import annotations

import logging
import sys
from typing import Any

logger = logging.getLogger(__name__)


class HandleErrors:
    """
    Error handler for MediaWiki API errors.

    Handles API error responses and converts them to appropriate
    exceptions or return values.
    """

    def __init__(self) -> None:
        """
        Initialize the error handler.
        """

    def handle_err(
        self,
        error: dict,
        function: str = "",
        params: dict | None = None,
        do_error: bool = True,
    ) -> dict[str, Any]:
        """
        Handle errors based on the provided error dictionary.
        """

        # {'error': {'code': 'articleexists', 'info': 'The article you tried to create has been created already.', '*': 'See https://ar.wikipedia.org/w/api.php for API usage. Subscribe to the mediawiki-api-announce mailing list at &lt;https://lists.wikimedia.org/postorius/lists/mediawiki-api-announce.lists.wikimedia.org/&gt; for notice of API deprecations and breaking changes.'}, 'servedby': 'mw1425'}

        err_code = error.get("code", "")
        err_info = error.get("info", "")

        tt = f"<<lightred>>{function} ERROR:code:{err_code}."
        logger.info(tt)

        # ["protectedpage", "تأخير البوتات 3 ساعات", False]

        if err_code == "abusefilter-disallowed":
            # oioioi = {'error': {'code': 'abusefilter-disallowed', 'info': 'This', 'abusefilter': {'id': '169', 'description': 'تأخير البوتات 3 ساعات', 'actions': ['disallow']}, '*': 'See https'}, 'servedby': 'mw1374'}

            abusefilter = error.get("abusefilter", "")
            description = abusefilter.get("description", "") if isinstance(abusefilter, dict) else ""
            logger.info(f"<<lightred>> ** abusefilter-disallowed: {description} ")
            if description in [
                "تأخير البوتات 3 ساعات",
                "تأخير البوتات 3 ساعات- 3 من 3",
                "تأخير البوتات 3 ساعات- 1 من 3",
                "تأخير البوتات 3 ساعات- 2 من 3",
            ]:
                # return False
                logger.debug(f"<<lightred>> ** abusefilter-disallowed: {description} ")
            return {"success": False, "error_code": err_code, "error": error}

        if err_code == "no-such-entity":
            logger.info("<<lightred>> ** no-such-entity. ")
            return {"success": False, "error_code": err_code, "error": error}

        if err_code == "protectedpage":
            logger.info("<<lightred>> ** protectedpage. ")
            return {"success": False, "error_code": err_code, "error": error}

        if err_code == "articleexists":
            logger.info("<<lightred>> ** article already created. ")
            # return "articleexists"
            return {"success": False, "error_code": err_code, "error": error}

        if err_code == "maxlag":
            logger.info("<<lightred>> ** maxlag. ")
            return {"success": False, "error_code": err_code, "error": error}

        if do_error:
            if params:
                params["data"] = {}
                params["text"] = {}
            logger.error(f"<<lightred>>{function} ERROR:info: {err_info}, {params=}")

        if "raise" in sys.argv:
            raise Exception(error)

        return {"success": False, "error_code": err_code, "error": error}


__all__ = [
    "HandleErrors",
]
