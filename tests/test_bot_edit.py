"""

python3 core8/pwb.py newapi/tests/test_bot_edit

"""
from newapi.page import MainPage

# ---
titles = [
    "أضرحة عائلة ميرزا أديغوزال بك",
    "موسى والراعي (قصة)",
    "جبل عمر",
    "ويكيبيديا:ملعب",
    "القدس خلال فترة الهيكل الثاني"
]
# ---
for x in titles:
    page = MainPage(x, "ar")

    canedit = page.can_edit(delay=30)

    # print(f"Page: {x}, \t:{canedit=}")
    # break
