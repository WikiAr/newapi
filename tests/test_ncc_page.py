"""
python3 core8/pwb.py newapi/tests/test_ncc_page nomwclient
python3 core8/pwb.py newapi/tests/test_ncc_page

wikiapi_new:
python3 core8/pwb.py newapi/tests/test_ncc_page wikiapi_new nomwclient
python3 core8/pwb.py newapi/tests/test_ncc_page wikiapi_new
"""
import sys

sys.argv.append("printurl")
sys.argv.append("ask")

if "wikiapi_new" in sys.argv:
    from wikiapi_new.ncc_page import MainPage, CatDepth, CatDepthLogin
else:
    from newapi.ncc_page import MainPage, CatDepth, CatDepthLogin

title = "Category:Pages_with_script_errors"

# CatDepthLogin()
# cat_members = CatDepth(title, depth=0, ns="10", nslist=[], tempyes=[])

CatDepthLogin(sitecode="www", family="nccommons")
cat_members = CatDepth(title, sitecode='www', family="nccommons", depth=0, onlyns=10)

# print(cat_members)
print(f"{len(cat_members)=}")

page = MainPage("Bilateral mesial temporal polymicrogyria (Radiopaedia 76456-88181 Axial SWI)", "www", family="nccommons")
# ---
text = page.get_text()
print(f"{len(text)=}")
