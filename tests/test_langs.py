"""

python3 core8/pwb.py newapi/tests/test_langs ask nomwclient
python3 core8/pwb.py newapi/tests/test_langs ask

"""

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
