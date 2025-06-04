"""

python3 core8/pwb.py newapi/tests/test_catdepth1 nomwclient
python3 core8/pwb.py newapi/tests/test_catdepth1
"""
import sys
# sys.argv.append("printurl")
sys.argv.append("ask")
from newapi.page import CatDepth1

cat_members = CatDepth1("اليمن", sitecode='ar', family="wikipedia", depth=0, ns="all", nslist=[], tempyes=[])

# print(cat_members.keys())
print(f"xxxxxxxxxxxxxx: {len(cat_members)=}")

cat_members2 = CatDepth1("Yemen", sitecode='en', family="wikipedia", depth=0, ns="all", nslist=[], tempyes=[])

# print(cat_members2.keys())
print(f"xxxxxxxxxxxxxx: {len(cat_members2)=}")

cat_members3 = CatDepth1("صنعاء", sitecode='ar', family="wikipedia", depth=0, ns="all", nslist=[], tempyes=[])

# print(cat_members3.keys())
print(f"xxxxxxxxxxxxxx: {len(cat_members3)=}")
