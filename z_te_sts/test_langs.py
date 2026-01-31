"""
Test runner usage: python3 core8/pwb.py newapi_bot/z_te_sts/test_runner
"""

import sys

from newapi.page import NEW_API, MainPage

sys.argv.append("printurl")
sys.argv.append("ask")


page = MainPage("وب:ملعب", "ar")
exists = page.exists()

# ---
print("--------------")
print("simple:")

# ---
en_api_new = NEW_API("simple", family="wikipedia")
# ---
# en_api_new.Login_to_wiki()
# ---
pages = en_api_new.Find_pages_exists_or_not(["yemen"])
# ---
print("--------------")
save_page = page.save(newtext="test!", summary="", nocreate=1, minor="")
