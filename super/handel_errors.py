"""
from .super.handel_errors import HANDEL_ERRORS

"""
import sys
# from newapi import printe
from ..api_utils import printe


class HANDEL_ERRORS:
    def __init__(self):
        # printe.output("class HANDEL_ERRORS:")
        pass

    def handel_err(self, error: dict, function: str = "", params: dict = None, do_error: bool = True):
        """Handle errors based on the provided error dictionary.

        This function processes an error dictionary and performs actions based
        on the error code. It checks for specific error codes and outputs
        relevant information. If the error code indicates that an article
        already exists or if the entity does not exist, it returns specific
        values. Additionally, it can log the error information if required. If
        the command line argument "raise" is present, it raises a generic
        exception with the error details.

        Args:
            error (dict): A dictionary containing error information.
            function (str?): The name of the function where the error occurred. Defaults to an empty
                string.
            params (dict?): A dictionary to hold additional parameters related to the error.
                Defaults to None.
            do_error (bool?): A flag to determine whether to log the error information. Defaults to
                True.

        Returns:
            Union[str, bool]: Returns specific strings for certain error codes or False for others.

        Raises:
            Exception: If the command line argument "raise" is present, raises a generic
                exception with the error details.
        """

        # ---
        # {'error': {'code': 'articleexists', 'info': 'The article you tried to create has been created already.', '*': 'See https://ar.wikipedia.org/w/api.php for API usage. Subscribe to the mediawiki-api-announce mailing list at &lt;https://lists.wikimedia.org/postorius/lists/mediawiki-api-announce.lists.wikimedia.org/&gt; for notice of API deprecations and breaking changes.'}, 'servedby': 'mw1425'}
        # ---
        err_code = error.get("code", "")
        err_info = error.get("info", "")
        # ---
        tt = f"<<lightred>>{function} ERROR: <<defaut>>code:{err_code}."
        # ---["protectedpage", 'تأخير البوتات 3 ساعات', False]
        if err_code == "abusefilter-disallowed":
            # ---
            # oioioi = {'error': {'code': 'abusefilter-disallowed', 'info': 'This', 'abusefilter': {'id': '169', 'description': 'تأخير البوتات 3 ساعات', 'actions': ['disallow']}, '*': 'See https'}, 'servedby': 'mw1374'}
            # ---
            abusefilter = error.get("abusefilter", "")
            description = abusefilter.get("description", "")
            printe.output(f"<<lightred>> ** abusefilter-disallowed: {description} ")
            if description in ["تأخير البوتات 3 ساعات", "تأخير البوتات 3 ساعات- 3 من 3", "تأخير البوتات 3 ساعات- 1 من 3", "تأخير البوتات 3 ساعات- 2 من 3"]:
                return False
            return description
        # ---
        if err_code == "no-such-entity":
            printe.output("<<lightred>> ** no-such-entity. ")
            return False
        # ---
        if err_code == "protectedpage":
            printe.output("<<lightred>> ** protectedpage. ")
            # return "protectedpage"
            return False
        # ---
        if err_code == "articleexists":
            printe.output("<<lightred>> ** article already created. ")
            return "articleexists"
        # ---
        if err_code == "maxlag":
            printe.output("<<lightred>> ** maxlag. ")
            return False
        # ---
        if do_error:
            params['data'] = {}
            params['text'] = {}
            printe.error(f"<<lightred>>{function} ERROR: <<defaut>>info: {err_info}, {params=}")
        # ---
        if "raise" in sys.argv:
            raise Exception(error)
