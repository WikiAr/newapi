"""
Test runner usage: python3 core8/pwb.py newapi_bot/z_te_sts/test_runner
"""

import sys
import time

sys.argv.append("printurl")
sys.argv.append("ask")

import logging

from newapi.page import NEW_API

logger = logging.getLogger(__name__)


class testmybot:
    def __init__(self):
        self.test = "test"
        self.api_new = NEW_API("en", family="wikipedia")
        # self.api_new.Login_to_wiki()

    def test1(self):
        """Find_pages_exists_or_not"""
        ex = self.api_new.Find_pages_exists_or_not(
            ["Thyrotropin alfa", "Thiamine"], get_redirect=True
        )
        return ex

    def test2(self):
        """Get_All_pages"""
        ex = self.api_new.Get_All_pages(start="!", limit_all=1000)
        return ex

    def test3(self):
        """Search"""
        ex = self.api_new.Search("yemen", srlimit="1000")
        return ex

    def test4(self):
        """Get_Newpages"""
        ex = self.api_new.Get_Newpages(limit=100)
        return ex

    def test5(self):
        """Get language links for a list of names.

        This method retrieves language links for a predefined list of names
        using the `Get_langlinks_for_list` API method. The list contains various
        individuals, and the function specifically targets the German language
        site code ("de"). The results are returned for further processing or
        validation.

        Returns:
            list: A list of language links corresponding to the input names.
        """
        lista = [
            "Amanda Seales",
            "Aria Mia Loberti",
            "Rachel Sennott",
            "Bassam Tariq",
            "Darius Marder",
            "Elvira Lind",
            "Shaka King",
            "Dev Hynes",
            "Michael Stipe",
            "Raveena Aurora",
            "Tommy Genesis",
            "Vic Mensa",
            "Becca Balint",
            "Earl Blumenauer",
            "Sanford Bishop",
            "Suzanne Bonamici",
            "Greg Casar",
            "Jason Crow",
            "Diana DeGette",
            "Chris Deluzio",
            "Mark DeSaulnier",
            "Debbie Dingell",
            "Veronica Escobar",
            "Valerie Foushee",
            "John Garamendi",
            "Chuy García",
            "Raúl Grijalva",
            "Josh Harder",
            "Chrissy Houlahan",
            "Dan Kildee",
            "Greg Landsman",
            "Summer Lee",
            "Teresa Leger Fernandez",
            "Zoe Lofgren",
            "Seth Magaziner",
            "Betty McCollum",
            "Morgan McGarvey",
            "Kweisi Mfume",
            "Donald Payne Jr.",
            "Chellie Pingree",
            "Pat Ryan (politician)",
            "Jamie Raskin",
            "Delia Ramirez",
            "Mary Gay Scanlon",
            "Jan Schakowsky",
            "Terri Sewell",
            "Brad Sherman",
            "Mikie Sherrill",
            "Paul Tonko",
            "Lauren Underwood",
            "Gabe Vasquez",
            "Nydia Velázquez",
            "Bonnie Watson Coleman",
        ]
        ex = self.api_new.Get_langlinks_for_list(lista, targtsitecode="de")
        return ex

    def test6(self):
        """UserContribs"""
        ex = self.api_new.UserContribs(
            "User:Mr. Ibahem", limit="10", namespace="*", ucshow=""
        )
        return ex

    def test7(self):
        """expandtemplates"""
        ex = self.api_new.expandtemplates("{{refn|Wing drop is an unc maneuvering.}}")
        return ex

    def test8(self):
        """get_extlinks"""
        api_new = NEW_API("ar", family="wikipedia")
        ex = api_new.get_extlinks("اليمن")
        return ex

    def test9(self):
        """querypage_list"""
        ex = self.api_new.querypage_list(
            qppage="Wantedcategories", qplimit="max", Max=500
        )
        return ex

    def test10(self):
        """Get_template_pages"""
        api_new = NEW_API("ar", family="wikipedia")
        ex = api_new.Get_template_pages(
            "قالب:طواف العالم للدراجات", namespace="*", Max=10000
        )
        return ex

    def test11(self):
        """move"""
        api_new = NEW_API("ar", family="wikipedia")
        move_it = api_new.move(
            "الصفحة_الرئيسة",
            "الصفحة_الرئيسة2",
            reason="test!",
            noredirect=False,
            movesubpages=False,
        )
        return move_it

    def test12(self):
        """Add_To_Bottom"""
        api_new = NEW_API("ar", family="wikipedia")
        move_it = api_new.Add_To_Bottom("x", "x", "الصفحة_الرئيسة")
        return move_it

    def test13(self):
        """get_pageassessments"""
        move_it = self.api_new.get_pageassessments("yemen")
        return move_it

    def test14(self):
        """users_infos"""
        api_new = NEW_API("ar", family="wikipedia")
        users = api_new.users_infos(ususers=["Mr. Ibrahem", "93.112.145.86"])

        return users

    def start(self):
        """Start the execution of defined test functions based on command-line
        arguments.

        This method initializes a dictionary of test functions and checks for
        command-line arguments to determine which tests to execute. It processes
        the arguments to filter the tests that should be run, executes them, and
        outputs the results. If a test function returns a dictionary, it formats
        and prints the results accordingly. Additionally, it handles specific
        command-line flags to control the output.

        Raises:
            Exception: If the result of a test function is an empty string.
        """

        # ---
        defs1 = {}
        # ---
        defs = {
            1: self.test1,
            2: self.test2,
            3: self.test3,
            4: self.test4,
            5: self.test5,
            6: self.test6,
            7: self.test7,
            8: self.test8,
            9: self.test9,
            10: self.test10,
            11: self.test11,
            12: self.test12,
            13: self.test13,
            14: self.test14,
        }
        # ---
        for arg in sys.argv:
            arg, _, value = arg.partition(":")
            if arg == "test" and value.isdigit():
                d = int(value)
                defs1[d] = defs[d]
        # ---
        if defs1 != {}:
            defs = defs1
        # ---
        for n, func in defs.items():
            name = func.__name__
            logger.info(f"<<lightgreen>> start def number {n}, name:{name}:")
            # ---
            def_name = func.__doc__
            logger.info(f"<<lightyellow>> test: {def_name}:")
            # ---
            if "tat" in sys.argv:
                continue
            # ---
            result = func()
            # ---
            # printe.output( result )
            # ---
            if isinstance(result, dict):
                for n, (na, ta) in enumerate(result.items()):
                    na2 = na  # f" '{na}' ".ljust(10)
                    # ---
                    if na == "claims":
                        for x, u in ta.items():
                            ta = {x: u}
                            break
                    # ---
                    # ta = json.dumps(ta, indent=2, ensure_ascii=False)
                    # ---
                    logger.info(f"{n}: {na2}: {ta}")
            # ---
            if result == "":
                raise Exception("result == ''")
            # ---
            if "printresult" in sys.argv:
                if isinstance(result, str):
                    logger.info(f"result:{result}")
                elif isinstance(result, list):
                    logger.info(result)
                else:
                    logger.info(result)
            else:
                logger.info("<<purple>> add 'printresult' to sys.argv to print result")
            # ---
            if result:
                logger.info(f"{len(result)=}")
            # ---
            logger.info("=====================")
            logger.info(f"<<lightyellow>> test: {def_name} end...")
            logger.info("time.sleep(1)")
            time.sleep(1)


if __name__ == "__main__":
    testmybot().start()
