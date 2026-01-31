import pytest

from newapi.api_utils.bot_edit.bot_edit_by_templates import is_bot_edit_allowed


def test_allowed_no_templates():
    text = """Some page text without any templates."""
    assert is_bot_edit_allowed(text, "Page1", "all") is True


def test_denied_by_stop_template():
    text = "{{تحرر}}\nSome text."
    assert is_bot_edit_allowed(text, "Page2", "all") is False


def test_denied_by_nobots():
    text = "{{nobots}}\nContent."
    assert is_bot_edit_allowed(text, "Page3", "all") is False


def test_allowed_by_bots_allow_all():
    text = "{{bots|allow=all}}"
    assert is_bot_edit_allowed(text, "Page4", "all") is True


def test_denied_by_bots_deny_all():
    text = "{{bots|deny=all}}"
    assert is_bot_edit_allowed(text, "Page5", "all") is False


def test_allowed_by_bots_allow_specific():
    text = "{{bots|allow=Mr.Ibrahembot}}"
    assert is_bot_edit_allowed(text, "Page6", "all") is True


def test_denied_by_bots_allow_other():
    text = "{{bots|allow=OtherBot}}"
    assert is_bot_edit_allowed(text, "Page7", "all") is False


def test_allowed_with_botedit_arg(monkeypatch):
    monkeypatch.setattr('sys.argv', ['botedit'])
    text = "{{تحرر}}"
    assert is_bot_edit_allowed(text, "Page8", "all") is True
