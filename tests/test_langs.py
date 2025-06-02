"""

python3 core8/pwb.py newapi/tests/test_langs nomwclient
python3 core8/pwb.py newapi/tests/test_langs

wikiapi_new:
python3 core8/pwb.py newapi/tests/test_langs wikiapi_new nomwclient
python3 core8/pwb.py newapi/tests/test_langs wikiapi_new

"""
import sys

sys.argv.append("printurl")
sys.argv.append("ask")

if "wikiapi_new" in sys.argv:
    from wikiapi_new.page import MainPage
else:
    from newapi.page import MainPage

page = MainPage('وب:ملعب', 'ar')
exists = page.exists()

# ---
print('--------------')
print('simple:')
from newapi.page import NEW_API

# ---
en_api_new = NEW_API('simple', family='wikipedia')
# ---
en_api_new.Login_to_wiki()
# ---
pages = en_api_new.Find_pages_exists_or_not(['yemen'])
# ---
print('--------------')
save_page = page.save(newtext='test!', summary='', nocreate=1, minor='')
