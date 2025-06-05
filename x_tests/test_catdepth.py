"""

python3 core8/pwb.py newapi_bot/x_tests/test_catdepth mwclient
python3 core8/pwb.py newapi_bot/x_tests/test_catdepth
"""
import sys
# sys.argv.append("printurl")
sys.argv.append("ask")
from newapi.page import CatDepth

cat_members = CatDepth("اليمن", sitecode='ar', family="wikipedia", depth=0, ns="all", nslist=[], tempyes=[])

# print(cat_members.keys())
print(f"xxxxxxxxxxxxxx: {len(cat_members)=}")

cat_members2 = CatDepth("Yemen", sitecode='en', family="wikipedia", depth=0, ns="all", nslist=[], tempyes=[])

# print(cat_members2.keys())
print(f"xxxxxxxxxxxxxx: {len(cat_members2)=}")

cat_members3 = CatDepth("صنعاء", sitecode='ar', family="wikipedia", depth=0, ns="all", nslist=[], tempyes=[])

# print(cat_members3.keys())
print(f"xxxxxxxxxxxxxx: {len(cat_members3)=}")
