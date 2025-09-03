"""
Test runner usage: python3 core8/pwb.py newapi_bot/x_tests/test_runner
"""
import sys

sys.argv.append("printurl")
sys.argv.append("ask")

from newapi.ncc_page import MainPage, CatDepth

title = "Category:Pages_with_script_errors"

# cat_members = CatDepth(title, depth=0, ns="10", nslist=[], tempyes=[])

cat_members = CatDepth(title, sitecode='www', family="nccommons", depth=0, onlyns=10)

# print(cat_members)
print(f"{len(cat_members)=}")

page = MainPage("Bilateral mesial temporal polymicrogyria (Radiopaedia 76456-88181 Axial SWI)", "www", family="nccommons")
# ---
text = page.get_text()
print(f"{len(text)=}")
