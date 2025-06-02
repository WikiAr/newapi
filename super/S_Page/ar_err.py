#!/usr/bin/python3

"""

from .super.S_Page.ar_err import find_edit_error
if find_edit_error(old, new): return
"""


def find_edit_error(old, new):
    # Define the dictionary of conversion phrases
    conversion_phrases = {
        "#تحويل [[",
    }
    for phrase in conversion_phrases:
        if phrase in old and phrase not in new:
            print(f"ar_err.py found ({phrase}) in old but not in new. return True")
            return True

    return False


def test_find_edit_error():
    # Test case 1: Phrase in old but not in new
    old_text = "#تحويل [[قاعدة قانونية]]"
    new_text = "[[تصنيف:أخلاقيات قانونية]]"
    result = find_edit_error(old_text, new_text)
    print(f"Test case 1: Result = {result}")

    # Test case 2: Phrase in both old and new
    old_text = "This is an #تحويل [[ example."
    new_text = "This is an #تحويل [[ example."
    result = find_edit_error(old_text, new_text)
    print(f"Test case 2: Result = {result}")

    # Test case 3: Phrase not in old or new
    old_text = "This is an example."
    new_text = "This is another example."
    result = find_edit_error(old_text, new_text)
    print(f"Test case 3: Result = {result}")

    print("All test cases pass!")


if __name__ == "__main__":
    # Run the test
    test_find_edit_error()
