"""
Comprehensive pytest-based unit tests for is_bot_edit_allowed function.

Tests cover various scenarios including:
- Template restrictions (nobots, bots, custom templates)
- Bot job types
- Parameter combinations
- Edge cases and special conditions
"""

import sys
from unittest.mock import MagicMock, patch

import pytest
from newapi.api_utils.bot_edit.bot_edit_by_templates import (
    Bot_Cache,
    is_bot_edit_allowed,
    stop_edit_temps,
)

# ==================== Fixtures ====================


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment before and after each test."""
    # Setup
    Bot_Cache.clear()
    original_argv = sys.argv.copy()
    sys.argv = ["test"]

    yield

    # Teardown
    Bot_Cache.clear()
    sys.argv = original_argv


@pytest.fixture
def mock_wtp():
    """Provide a mocked wikitextparser."""
    with patch("newapi.api_utils.bot_edit.bot_edit_by_templates.wtp") as mock:
        yield mock


@pytest.fixture
def create_mock_template():
    """Factory fixture for creating mock templates."""

    def _create_template(name, arguments=None):
        mock_template = MagicMock()
        mock_template.normal_name.return_value = name
        mock_template.string = f"{{{{{name}}}}}"

        if arguments is None:
            mock_template.arguments = []
        else:
            mock_params = []
            for param_name, param_value in arguments.items():
                mock_param = MagicMock()
                mock_param.name = param_name
                mock_param.value = param_value
                mock_params.append(mock_param)
            mock_template.arguments = mock_params

        return mock_template

    return _create_template


@pytest.fixture
def setup_parser(mock_wtp, create_mock_template):
    """Factory fixture for setting up parser with templates."""

    def _setup(templates_config):
        templates = []
        for config in templates_config:
            if isinstance(config, dict):
                name = config.get("name")
                arguments = config.get("arguments")
                templates.append(create_mock_template(name, arguments))
            else:
                # If just a string, create template with that name
                templates.append(create_mock_template(config))

        mock_parser = MagicMock()
        mock_parser.templates = templates
        mock_wtp.parse.return_value = mock_parser

        return mock_parser

    return _setup


# ==================== Basic Functionality Tests ====================


class TestBasicFunctionality:
    """Test basic functionality of is_bot_edit_allowed."""

    def test_empty_text_allows_edit(self):
        """Test that empty text allows bot editing."""
        result = is_bot_edit_allowed(text="", title_page="Test Page", botjob="all")
        assert result is True

    def test_plain_text_allows_edit(self):
        """Test that plain text without templates allows bot editing."""
        text = "This is just plain text without any templates."
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is True

    def test_default_botjob_parameter(self):
        """Test that empty botjob defaults to 'all'."""
        text = "Plain text"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="")
        assert result is True
        assert "all" in Bot_Cache

    def test_fixref_cat_stub_tempcat_portal_defaults_to_all(self):
        """Test that combined botjob string defaults to 'all'."""
        text = "Plain text"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="fixref|cat|stub|tempcat|portal")
        assert result is True
        assert "all" in Bot_Cache


# ==================== Cache Tests ====================


class TestCacheBehavior:
    """Test cache behavior and management."""

    def test_cache_hit_returns_cached_value(self):
        """Test that cached results are returned on subsequent calls."""
        text = "Plain text"
        title = "Test Page"
        botjob = "all"

        # First call - should process and cache
        result1 = is_bot_edit_allowed(text=text, title_page=title, botjob=botjob)

        # Second call - should use cache
        result2 = is_bot_edit_allowed(text=text, title_page=title, botjob=botjob)

        assert result1 == result2
        assert botjob in Bot_Cache
        assert title in Bot_Cache[botjob]

    def test_cache_separate_for_different_botjobs(self):
        """Test that cache is separate for different bot jobs."""
        text = "Plain text"
        title = "Test Page"

        result1 = is_bot_edit_allowed(text=text, title_page=title, botjob="all")
        result2 = is_bot_edit_allowed(text=text, title_page=title, botjob="cat")

        assert "all" in Bot_Cache
        assert "cat" in Bot_Cache

    def test_cache_structure_created_correctly(self):
        """Test that cache structure is created correctly for new botjobs."""
        is_bot_edit_allowed(text="", title_page="Page1", botjob="cat")
        assert "cat" in Bot_Cache
        assert isinstance(Bot_Cache["cat"], dict)

    def test_multiple_pages_cached_separately(self):
        """Test that different pages are cached separately."""
        is_bot_edit_allowed(text="", title_page="Page1", botjob="all")
        is_bot_edit_allowed(text="", title_page="Page2", botjob="all")

        assert "Page1" in Bot_Cache["all"]
        assert "Page2" in Bot_Cache["all"]

    def test_cache_persists_across_calls(self):
        """Test that cache persists across multiple function calls."""
        page = "Test Page"
        botjob = "all"

        # First call
        is_bot_edit_allowed(text="", title_page=page, botjob=botjob)
        first_cache_value = Bot_Cache[botjob][page]

        # Second call
        is_bot_edit_allowed(text="", title_page=page, botjob=botjob)
        second_cache_value = Bot_Cache[botjob][page]

        assert first_cache_value == second_cache_value


# ==================== Nobots Template Tests ====================


class TestNobotsTemplate:
    """Test nobots template handling."""

    def test_nobots_without_params_denies_edit(self, setup_parser):
        """Test that {{nobots}} without parameters denies editing."""
        setup_parser([{"name": "nobots", "arguments": None}])

        text = "{{nobots}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is False

    def test_nobots_with_all_denies_edit(self, setup_parser):
        """Test that {{nobots|1=all}} denies editing."""
        setup_parser([{"name": "nobots", "arguments": {"1": "all"}}])

        text = "{{nobots|1=all}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is False

    def test_nobots_with_specific_bot_denies_edit(self, setup_parser):
        """Test that {{nobots|1=Mr.Ibrahembot}} denies editing."""
        setup_parser([{"name": "nobots", "arguments": {"1": "Mr.Ibrahembot"}}])

        text = "{{nobots|1=Mr.Ibrahembot}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is False

    def test_nobots_with_bot_list_including_our_bot_denies(self, setup_parser):
        """Test that {{nobots|1=Bot1,Mr.Ibrahembot,Bot2}} denies editing."""
        setup_parser([{"name": "nobots", "arguments": {"1": "Bot1,Mr.Ibrahembot,Bot2"}}])

        text = "{{nobots|1=Bot1,Mr.Ibrahembot,Bot2}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is False

    def test_nobots_with_other_bots_allows_edit(self, setup_parser):
        """Test that {{nobots|1=OtherBot}} allows editing."""
        setup_parser([{"name": "nobots", "arguments": {"1": "OtherBot,AnotherBot"}}])

        text = "{{nobots|1=OtherBot,AnotherBot}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is True

    def test_nobots_case_insensitive(self, setup_parser):
        """Test that nobots template matching is case insensitive."""
        setup_parser([{"name": "NoBots", "arguments": None}])

        text = "{{NoBots}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is False

    def test_nobots_with_whitespace_in_bot_names(self, setup_parser):
        """Test handling of whitespace in bot name lists."""
        setup_parser([{"name": "nobots", "arguments": {"1": " Bot1 , Mr.Ibrahembot , Bot2 "}}])

        text = "{{nobots|1= Bot1 , Mr.Ibrahembot , Bot2 }}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is False


# ==================== Bots Template Tests ====================


class TestBotsTemplate:
    """Test bots template handling."""

    def test_bots_without_params_denies_edit(self, setup_parser):
        """Test that {{bots}} without parameters denies editing."""
        setup_parser([{"name": "bots", "arguments": None}])

        text = "{{bots}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is False

    def test_bots_allow_all_allows_edit(self, setup_parser):
        """Test that {{bots|allow=all}} allows editing."""
        setup_parser([{"name": "bots", "arguments": {"allow": "all"}}])

        text = "{{bots|allow=all}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is True

    def test_bots_allow_specific_bot_allows_edit(self, setup_parser):
        """Test that {{bots|allow=Mr.Ibrahembot}} allows editing."""
        setup_parser([{"name": "bots", "arguments": {"allow": "Mr.Ibrahembot"}}])

        text = "{{bots|allow=Mr.Ibrahembot}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is True

    def test_bots_allow_bot_list_including_our_bot_allows(self, setup_parser):
        """Test that {{bots|allow=Bot1,Mr.Ibrahembot,Bot2}} allows editing."""
        setup_parser([{"name": "bots", "arguments": {"allow": "Bot1,Mr.Ibrahembot,Bot2"}}])

        text = "{{bots|allow=Bot1,Mr.Ibrahembot,Bot2}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is True

    def test_bots_allow_none_denies_edit(self, setup_parser):
        """Test that {{bots|allow=none}} denies editing."""
        setup_parser([{"name": "bots", "arguments": {"allow": "none"}}])

        text = "{{bots|allow=none}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is False

    def test_bots_allow_other_bots_denies_edit(self, setup_parser):
        """Test that {{bots|allow=OtherBot}} denies editing."""
        setup_parser([{"name": "bots", "arguments": {"allow": "OtherBot,AnotherBot"}}])

        text = "{{bots|allow=OtherBot,AnotherBot}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is False

    def test_bots_deny_all_denies_edit(self, setup_parser):
        """Test that {{bots|deny=all}} denies editing."""
        setup_parser([{"name": "bots", "arguments": {"deny": "all"}}])

        text = "{{bots|deny=all}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is False

    def test_bots_deny_specific_bot_denies_edit(self, setup_parser):
        """Test that {{bots|deny=Mr.Ibrahembot}} denies editing."""
        setup_parser([{"name": "bots", "arguments": {"deny": "Mr.Ibrahembot"}}])

        text = "{{bots|deny=Mr.Ibrahembot}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is False

    def test_bots_deny_other_bots_allows_edit(self, setup_parser):
        """Test that {{bots|deny=OtherBot}} allows editing."""
        setup_parser([{"name": "bots", "arguments": {"deny": "OtherBot,AnotherBot"}}])

        text = "{{bots|deny=OtherBot,AnotherBot}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is True

    def test_bots_case_insensitive(self, setup_parser):
        """Test that bots template matching is case insensitive."""
        setup_parser([{"name": "Bots", "arguments": {"allow": "all"}}])

        text = "{{Bots|allow=all}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is True


# ==================== Stop Edit Templates Tests ====================


class TestStopEditTemplates:
    """Test stop edit templates handling."""

    @pytest.mark.parametrize("template_name", stop_edit_temps["all"])
    def test_global_stop_templates_deny_edit(self, template_name, setup_parser):
        """Test that global stop templates deny editing."""
        setup_parser([{"name": template_name, "arguments": None}])

        text = f"{{{{{template_name}}}}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is False

    def test_specific_botjob_stop_template_denies_edit(self, setup_parser):
        """Test that job-specific stop templates deny editing."""
        # Test تعريب job with its specific template
        setup_parser([{"name": "لا للتعريب", "arguments": None}])

        text = "{{لا للتعريب}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="تعريب")
        assert result is False

    def test_stop_template_for_different_botjob_allows_edit(self, setup_parser):
        """Test that stop templates for different bot jobs allow editing."""
        # Template for تعريب job, but we're running cat job
        setup_parser([{"name": "لا للتعريب", "arguments": None}])

        text = "{{لا للتعريب}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="cat")
        assert result is True

    @pytest.mark.parametrize(
        "botjob,template_list", [(job, templates) for job, templates in stop_edit_temps.items() if job != "all"]
    )
    def test_all_stop_templates_for_each_botjob(self, botjob, template_list, setup_parser):
        """Test all stop templates for each specific bot job."""
        for template_name in template_list:
            Bot_Cache.clear()
            setup_parser([{"name": template_name, "arguments": None}])

            text = f"{{{{{template_name}}}}}"
            result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob=botjob)
            assert result is False, f"Template {template_name} should deny {botjob}"


# ==================== Multiple Templates Tests ====================


class TestMultipleTemplates:
    """Test handling of multiple templates."""

    def test_multiple_templates_first_restricting_denies(self, setup_parser):
        """Test that first restricting template denies editing."""
        setup_parser([{"name": "nobots", "arguments": None}, {"name": "some_other_template", "arguments": None}])

        text = "{{nobots}} {{some_other_template}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is False

    def test_multiple_non_restricting_templates_allows(self, setup_parser):
        """Test that multiple non-restricting templates allow editing."""
        setup_parser([{"name": "infobox", "arguments": None}, {"name": "citation", "arguments": None}])

        text = "{{infobox}} {{citation}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is True


# ==================== Edge Cases Tests ====================


class TestEdgeCases:
    """Test edge cases and special conditions."""

    def test_empty_template_parameters(self, setup_parser):
        """Test handling of templates with empty parameter values."""
        setup_parser([{"name": "nobots", "arguments": {"1": ""}}])

        text = "{{nobots|1=}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        # Empty params should be treated as no params
        assert result is False

    def test_template_with_multiple_parameters(self, setup_parser):
        """Test template with multiple parameters."""
        setup_parser([{"name": "bots", "arguments": {"allow": "all", "other_param": "some_value"}}])

        text = "{{bots|allow=all|other_param=some_value}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is True

    def test_parameter_filtering_empty_values(self, setup_parser):
        """Test that parameters with empty values are filtered out."""
        setup_parser([{"name": "bots", "arguments": {"allow": "all", "empty_param": ""}}])

        text = "{{bots|allow=all|empty_param=}}"
        result = is_bot_edit_allowed(text=text, title_page="Test Page", botjob="all")
        assert result is True


# ==================== Parametrized Test Collections ====================


class TestParametrizedScenarios:
    """Parametrized tests for various scenarios."""

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("", True),
            ("Plain text", True),
            ("Some content without templates", True),
        ],
    )
    def test_non_template_text_allows_editing(self, text, expected):
        """Test that non-template text allows editing."""
        result = is_bot_edit_allowed(text=text, title_page="Test", botjob="all")
        assert result == expected

    @pytest.mark.parametrize("botjob", ["all", "cat", "stub", "portal", "fixref"])
    def test_cache_initialized_for_different_botjobs(self, botjob):
        """Test that cache is initialized for different botjobs."""
        is_bot_edit_allowed(text="", title_page="Test", botjob=botjob)
        expected_job = "all" if botjob in ["", "fixref|cat|stub|tempcat|portal"] else botjob
        assert expected_job in Bot_Cache

    @pytest.mark.parametrize(
        "bot_list,should_allow",
        [
            ("OtherBot", True),
            ("Bot1,Bot2,Bot3", True),
            ("Mr.Ibrahembot", False),
            ("Bot1,Mr.Ibrahembot", False),
            ("all", False),
        ],
    )
    def test_nobots_with_various_bot_lists(self, bot_list, should_allow, setup_parser):
        """Test nobots template with various bot lists."""
        setup_parser([{"name": "nobots", "arguments": {"1": bot_list}}])

        result = is_bot_edit_allowed(text="{{nobots}}", title_page="Test", botjob="all")
        assert result == should_allow

    @pytest.mark.parametrize(
        "allow_list,should_allow",
        [
            ("all", True),
            ("Mr.Ibrahembot", True),
            ("Bot1,Mr.Ibrahembot,Bot2", True),
            ("none", False),
            ("OtherBot", False),
        ],
    )
    def test_bots_allow_with_various_lists(self, allow_list, should_allow, setup_parser):
        """Test bots allow parameter with various lists."""
        setup_parser([{"name": "bots", "arguments": {"allow": allow_list}}])

        result = is_bot_edit_allowed(text="{{bots}}", title_page="Test", botjob="all")
        assert result == should_allow

    @pytest.mark.parametrize(
        "deny_list,should_allow",
        [
            ("all", False),
            ("Mr.Ibrahembot", False),
            ("Bot1,Mr.Ibrahembot,Bot2", False),
            ("OtherBot", True),
            ("Bot1,Bot2", True),
        ],
    )
    def test_bots_deny_with_various_lists(self, deny_list, should_allow, setup_parser):
        """Test bots deny parameter with various lists."""
        setup_parser([{"name": "bots", "arguments": {"deny": deny_list}}])

        result = is_bot_edit_allowed(text="{{bots}}", title_page="Test", botjob="all")
        assert result == should_allow


# ==================== Integration Tests ====================


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_workflow_allowed(self, setup_parser):
        """Test complete workflow where editing is allowed."""
        # Setup non-restricting template
        setup_parser([{"name": "infobox", "arguments": None}])

        # First call - process and cache
        result1 = is_bot_edit_allowed(text="{{infobox}}", title_page="Article", botjob="all")

        # Second call - use cache
        result2 = is_bot_edit_allowed(text="{{infobox}}", title_page="Article", botjob="all")

        assert result1 is True
        assert result2 is True
        assert "Article" in Bot_Cache["all"]
        assert Bot_Cache["all"]["Article"] is True

    def test_complete_workflow_denied(self, setup_parser):
        """Test complete workflow where editing is denied."""
        # Setup restricting template
        setup_parser([{"name": "nobots", "arguments": None}])

        # First call - process and cache
        result1 = is_bot_edit_allowed(text="{{nobots}}", title_page="Article", botjob="all")

        # Second call - use cache
        result2 = is_bot_edit_allowed(text="{{nobots}}", title_page="Article", botjob="all")

        assert result1 is False
        assert result2 is False
        assert "Article" in Bot_Cache["all"]
        assert Bot_Cache["all"]["Article"] is False

    def test_different_pages_different_results(self, setup_parser):
        """Test that different pages can have different results."""
        # Page 1 - allowed
        setup_parser([{"name": "infobox", "arguments": None}])
        result1 = is_bot_edit_allowed(text="{{infobox}}", title_page="Page1", botjob="all")

        # Page 2 - denied
        setup_parser([{"name": "nobots", "arguments": None}])
        result2 = is_bot_edit_allowed(text="{{nobots}}", title_page="Page2", botjob="all")

        assert result1 is True
        assert result2 is False
        assert Bot_Cache["all"]["Page1"] is True
        assert Bot_Cache["all"]["Page2"] is False


# ==================== Performance and Special Cases ====================


class TestSpecialCases:
    """Test special cases and boundary conditions."""

    def test_very_long_bot_list(self, setup_parser):
        """Test handling of very long bot lists."""
        long_list = ",".join([f"Bot{i}" for i in range(100)])
        setup_parser([{"name": "nobots", "arguments": {"1": long_list}}])

        result = is_bot_edit_allowed(text="{{nobots}}", title_page="Test", botjob="all")
        assert result is True  # Our bot not in the list

    def test_unicode_bot_names(self, setup_parser):
        """Test handling of unicode characters in bot names."""
        setup_parser([{"name": "nobots", "arguments": {"1": "بوت1,بوت2"}}])

        result = is_bot_edit_allowed(text="{{nobots}}", title_page="Test", botjob="all")
        assert result is True  # Our bot not in the list

    def test_mixed_case_template_names(self, setup_parser):
        """Test that template name matching works with mixed case."""
        for name in ["nobots", "Nobots", "NOBOTS", "nObOtS"]:
            Bot_Cache.clear()
            setup_parser([{"name": name, "arguments": None}])

            result = is_bot_edit_allowed(text=f"{{{{{name}}}}}", title_page="Test", botjob="all")
            assert result is False, f"Should deny for template name: {name}"


# ==================== Pytest Marks and Markers ====================


class TestSmokeTests:
    """Quick smoke tests for CI/CD."""

    def test_basic_allow(self):
        """Basic allow scenario."""
        assert is_bot_edit_allowed("", "Test", "all") is True

    def test_basic_deny(self, setup_parser):
        """Basic deny scenario."""
        setup_parser([{"name": "nobots", "arguments": None}])
        assert is_bot_edit_allowed("{{nobots}}", "Test", "all") is False

    def test_cache_works(self):
        """Cache functionality works."""
        is_bot_edit_allowed("", "Test", "all")
        assert "all" in Bot_Cache
        assert "Test" in Bot_Cache["all"]
