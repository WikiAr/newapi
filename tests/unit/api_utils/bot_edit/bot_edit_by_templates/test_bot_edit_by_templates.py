"""
Unit tests for is_bot_edit_allowed function.

Tests cover all scenarios including template restrictions,
caching behavior, and special template handling (nobots, bots).
"""

import sys

import pytest
from newapi.api_utils.bot_edit.bot_edit_by_templates import (
    Bot_Cache,
    edit_username,
    is_bot_edit_allowed,
    stop_edit_temps,
)


# Fixtures
@pytest.fixture(autouse=True)
def clear_bot_cache():
    """Clear the Bot_Cache before each test to ensure test isolation."""
    Bot_Cache.clear()
    yield
    Bot_Cache.clear()


@pytest.fixture
def original_argv():
    """Store and restore original sys.argv."""
    original = sys.argv.copy()
    yield original
    sys.argv = original


@pytest.fixture
def bot_username():
    """Return the bot username for testing."""
    return edit_username.get(1, "Mr.Ibrahembot")


# Test bot job normalization
class TestBotJobNormalization:
    """Test cases for bot job parameter normalization."""

    def test_empty_botjob_normalized_to_all(self, original_argv):
        """Empty string botjob should be normalized to 'all'."""
        sys.argv = ["script"]
        text = "some text"
        is_bot_edit_allowed(text=text, title_page="Test1", botjob="")
        assert "all" in Bot_Cache

    def test_combined_botjob_normalized_to_all(self, original_argv):
        """Combined botjob string should be normalized to 'all'."""
        sys.argv = ["script"]
        text = "some text"
        is_bot_edit_allowed(text=text, title_page="Test2", botjob="fixref|cat|stub|tempcat|portal")
        assert "all" in Bot_Cache

    def test_normal_botjob_preserved(self, original_argv):
        """Normal botjob values should be preserved."""
        sys.argv = ["script"]
        text = "some text"
        botjob = "تعريب"
        is_bot_edit_allowed(text=text, title_page="Test3", botjob=botjob)
        assert botjob in Bot_Cache


# Test caching behavior
class TestCaching:
    """Test cases for result caching functionality."""

    def test_cache_hit_returns_cached_value(self, original_argv, bot_username):
        """Subsequent calls should return cached value."""
        sys.argv = ["script"]
        text = f"{{{{nobots|{bot_username}}}}}"
        title = "CachedTest"

        # First call - should compute and cache
        result1 = is_bot_edit_allowed(text=text, title_page=title, botjob="all")
        # Second call - should return cached value
        result2 = is_bot_edit_allowed(text=text, title_page=title, botjob="all")

        assert result1 == result2
        assert Bot_Cache["all"][title] == result1

    def test_cache_key_includes_botjob(self, original_argv):
        """Different botjob values should have separate cache entries."""
        sys.argv = ["script"]
        text = "some text"
        title = "MultiJobTest"

        is_bot_edit_allowed(text=text, title_page=title, botjob="all")
        is_bot_edit_allowed(text=text, title_page=title, botjob="تعريب")

        assert "all" in Bot_Cache
        assert "تعريب" in Bot_Cache
        assert title in Bot_Cache["all"]
        assert title in Bot_Cache["تعريب"]


# Test stop templates
class TestStopTemplates:
    """Test cases for stop_edit_temps restrictions."""

    def test_all_stop_templates_block_edit(self, original_argv):
        """Templates in 'all' stop list should block editing."""
        sys.argv = ["script"]
        for template in stop_edit_temps["all"]:
            text = f"{{{{{template}}}}}"
            assert not is_bot_edit_allowed(
                text=text, title_page=f"Test_{template}", botjob="all"
            ), f"Template '{template}' should block editing for 'all' botjob"

    def test_botjob_specific_stop_templates(self, original_argv):
        """Templates in botjob-specific stop list should block editing."""
        sys.argv = ["script"]
        for botjob, templates in stop_edit_temps.items():
            if botjob == "all":
                continue
            for template in templates:
                text = f"{{{{{template}}}}}"
                assert not is_bot_edit_allowed(
                    text=text, title_page=f"Test_{botjob}_{template}", botjob=botjob
                ), f"Template '{template}' should block editing for '{botjob}' botjob"

    def test_other_templates_dont_block_edit(self, original_argv):
        """Templates not in stop lists should not block editing."""
        sys.argv = ["script"]
        text = "{{infobox}}"
        assert is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_nested_template_in_text(self, original_argv):
        """Should detect templates even when embedded in other text."""
        sys.argv = ["script"]
        text = "Some text {{تحرر}} more text"
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")


# Test nobots template
class TestNobotsTemplate:
    """Test cases for {{nobots}} template handling."""

    def test_nobots_no_params_blocks_all(self, original_argv):
        """{{nobots}} with no parameters should block all bots."""
        sys.argv = ["script"]
        text = "{{nobots}}"
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_nobots_with_all_blocks(self, original_argv):
        """{{nobots|all}} should block all bots."""
        sys.argv = ["script"]
        text = "{{nobots|all}}"
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_nobots_with_bot_username_blocks(self, original_argv, bot_username):
        """{{nobots|botname}} should block the specified bot."""
        sys.argv = ["script"]
        text = f"{{{{nobots|{bot_username}}}}}"
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_nobots_with_multiple_bots_including_ours(self, original_argv, bot_username):
        """{{nobots|bot1,bot2,ours}} should block if our bot is listed."""
        sys.argv = ["script"]
        text = f"{{{{nobots|OtherBot,{bot_username}}}}}"
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_nobots_with_other_bots_allows_ours(self, original_argv, bot_username):
        """{{nobots|OtherBot}} should allow our bot."""
        sys.argv = ["script"]
        text = "{{nobots|OtherBot}}"
        assert is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_nobots_case_insensitive(self, original_argv):
        """Template name should be case-insensitive."""
        sys.argv = ["script"]
        for variant in ["{{nobots}}", "{{NoBots}}", "{{NOBOTS}}", "{{NoBoTs}}"]:
            text = variant
            assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_nobots_whitespace_handling(self, original_argv):
        """Should handle whitespace in parameters."""
        sys.argv = ["script"]
        text = "{{nobots| all , OtherBot }}"
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_nobots_empty_param_blocks_all(self, original_argv):
        """{{Nobots|}} with empty parameter should block all bots."""
        sys.argv = ["script"]
        text = "{{Nobots|}}"
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")


# Test bots template
class TestBotsTemplate:
    """Test cases for {{bots}} template handling."""

    def test_bots_no_params_blocks(self, original_argv):
        """{{bots}} with no parameters should deny all bots."""
        sys.argv = ["script"]
        text = "{{bots}}"
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_bots_allow_all(self, original_argv):
        """{{bots|allow=all}} should allow all bots."""
        sys.argv = ["script"]
        text = "{{bots|allow=all}}"
        assert is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_bots_allow_bot_username(self, original_argv, bot_username):
        """{{bots|allow=botname}} should allow the specified bot."""
        sys.argv = ["script"]
        text = f"{{{{bots|allow={bot_username}}}}}"
        assert is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_bots_allow_multiple_bots_including_ours(self, original_argv, bot_username):
        """{{bots|allow=bot1,bot2,ours}} should allow if our bot is listed."""
        sys.argv = ["script"]
        text = f"{{{{bots|allow=OtherBot,{bot_username}}}}}"
        assert is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_bots_allow_other_bots_denies_ours(self, original_argv, bot_username):
        """{{bots|allow=OtherBot}} should deny our bot."""
        sys.argv = ["script"]
        text = "{{bots|allow=OtherBot}}"
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_bots_deny_all(self, original_argv):
        """{{bots|deny=all}} should deny all bots."""
        sys.argv = ["script"]
        text = "{{bots|deny=all}}"
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_bots_deny_bot_username(self, original_argv, bot_username):
        """{{bots|deny=botname}} should deny the specified bot."""
        sys.argv = ["script"]
        text = f"{{{{bots|deny={bot_username}}}}}"
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_bots_deny_other_bots_allows_ours(self, original_argv, bot_username):
        """{{bots|deny=OtherBot}} should allow our bot."""
        sys.argv = ["script"]
        text = "{{bots|deny=OtherBot}}"
        assert is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_bots_deny_multiple_bots_including_ours(self, original_argv, bot_username):
        """{{bots|deny=bot1,bot2,ours}} should deny if our bot is listed."""
        sys.argv = ["script"]
        text = f"{{{{bots|deny=OtherBot,{bot_username}}}}}"
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_bots_case_insensitive(self, original_argv):
        """Template name should be case-insensitive."""
        sys.argv = ["script"]
        for variant in ["{{bots}}", "{{Bots}}", "{{BOTS}}"]:
            text = variant
            assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_bots_whitespace_handling(self, original_argv):
        """Should handle whitespace in allow/deny parameters."""
        sys.argv = ["script"]
        text = "{{bots|allow= all , OtherBot }}"
        assert is_bot_edit_allowed(text=text, title_page="Test", botjob="all")


# Test default behavior
class TestDefaultBehavior:
    """Test cases for default behavior when no restrictions are found."""

    def test_empty_text_allows_edit(self, original_argv):
        """Empty text should allow editing."""
        sys.argv = ["script"]
        assert is_bot_edit_allowed(text="", title_page="Test", botjob="all")

    def test_no_templates_allows_edit(self, original_argv):
        """Text with no templates should allow editing."""
        sys.argv = ["script"]
        text = "This is just plain text with no templates."
        assert is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_harmless_templates_allows_edit(self, original_argv):
        """Text with harmless templates should allow editing."""
        sys.argv = ["script"]
        text = "{{infobox}} {{cite web}} some content"
        assert is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_multiple_templates_all_except_restrictions(self, original_argv):
        """Multiple templates should be checked until restriction found."""
        sys.argv = ["script"]
        text = "{{infobox}} {{cite web}} {{nobots}}"
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")


# Test edge cases
class TestEdgeCases:
    """Test cases for edge cases and special scenarios."""

    def test_template_with_parameters(self, original_argv):
        """Templates with parameters should be handled correctly."""
        sys.argv = ["script"]
        text = "{{تحرر|param1=value1}}"
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_malformed_template(self, original_argv):
        """Malformed templates should not crash the function."""
        sys.argv = ["script"]
        text = "{{broken template"
        # Should not raise exception, just allow edit
        assert is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_nested_templates(self, original_argv):
        """Nested templates should be processed."""
        sys.argv = ["script"]
        text = "{{outer template {{nobots}} }}"
        # wikitextparser should find the inner template
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_empty_params_in_nobots(self, original_argv):
        """Empty parameter in nobots should be handled."""
        sys.argv = ["script"]
        text = "{{nobots|}}"
        # Empty param means no list, so should block all
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="all")

    def test_unicode_in_params(self, original_argv):
        """Unicode characters in parameters should work correctly."""
        sys.argv = ["script"]
        text = "{{nobots|SomeBot,أخرى}}"
        # Our bot is not in the list
        assert is_bot_edit_allowed(text=text, title_page="Test", botjob="all")


# Test Arabic-specific stop templates
class TestArabicStopTemplates:
    """Test cases specifically for Arabic stop templates."""

    def test_arabic_all_stop_templates(self, original_argv):
        """Test all Arabic stop templates in the 'all' list."""
        sys.argv = ["script"]
        arabic_templates = ["تحرر", "قيد التطوير", "يحرر", "تطوير مقالة"]
        for template in arabic_templates:
            text = f"{{{{{template}}}}}"
            assert not is_bot_edit_allowed(
                text=text, title_page=f"Test_{template}", botjob="all"
            ), f"Arabic template '{template}' should block editing"

    def test_arabic_specific_botjob_templates(self, original_argv):
        """Test Arabic templates for specific bot jobs."""
        sys.argv = ["script"]

        test_cases = [
            ("تعريب", "لا للتعريب"),
            ("تقييم آلي", "لا للتقييم الآلي"),
            ("reftitle", "لا لعنونة مرجع غير معنون"),
            ("fixref", "لا لصيانة المراجع"),
            ("cat", "لا للتصنيف المعادل"),
            ("stub", "لا لتخصيص البذرة"),
            ("tempcat", "لا لإضافة صناديق تصفح معادلة"),
            ("portal", "لا لربط البوابات المعادل"),
        ]

        for botjob, template in test_cases:
            text = f"{{{{{template}}}}}"
            assert not is_bot_edit_allowed(
                text=text, title_page=f"Test_{botjob}_{template}", botjob=botjob
            ), f"Template '{template}' should block editing for '{botjob}'"

    def test_different_botjob_not_affected_by_specific_template(self, original_argv):
        """A template specific to one botjob should not affect other botjobs."""
        sys.argv = ["script"]
        text = "{{لا للتعريب}}"
        # Should block for 'تعريب' botjob
        assert not is_bot_edit_allowed(text=text, title_page="Test", botjob="تعريب")
        # Should allow for 'all' botjob (not in 'all' stop list)
        assert is_bot_edit_allowed(text=text, title_page="Test2", botjob="all")
