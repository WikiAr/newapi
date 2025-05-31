"""

python3 core8/pwb.py newapi/tests/test_bot_edit

I:/core/bots/new/newapi/tests/‏‏test_bot_edit.py

"""
from newapi.page import MainPage

# ---
titles = [
    "أضرحة عائلة ميرزا أديغوزال بك",
    "موسى والراعي (قصة)",
    "جبل عمر",
    "ويكيبيديا:ملعب",
    "القدس خلال فترة الهيكل الثاني",
    "أضرحة عائلة ميرزا أديغوزال بك",
]
# ---
for x in titles:
    page = MainPage(x, "ar")

    canedit = page.can_edit(delay=30)

    # print(f"Page: {x}, \t:{canedit=}")
    # break
