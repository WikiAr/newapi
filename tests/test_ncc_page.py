"""
python3 core8/pwb.py newapi/tests/test_ncc_page nomwclient
python3 core8/pwb.py newapi/tests/test_ncc_page
"""
from newapi.ncc_page import CatDepth, CatDepthLogin

title = "Category:Pages_with_script_errors"

# CatDepthLogin()
# cat_members = CatDepth(title, depth=0, ns="10", nslist=[], tempyes=[])

CatDepthLogin(sitecode="www", family="nccommons")
cat_members = CatDepth(title, sitecode='www', family="nccommons", depth=0, onlyns=10)

# print(cat_members)
print(f"{len(cat_members)=}")
